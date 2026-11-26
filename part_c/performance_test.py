"""Performance experiments for CREATE, UPDATE, and DELETE Todo operations.

The script measures API transaction time only. Object generation and fixture
creation for UPDATE/DELETE are deliberately outside the timed region.

Examples:
    python -m part_c.performance_test
    python -m part_c.performance_test --sizes 100,500,1000,2000,5000 --repeats 5
    python -m part_c.performance_test --operations create,update
"""
from __future__ import annotations

import argparse
import csv
import random
import string
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import requests


DEFAULT_BASE_URL = "http://localhost:4567"
DEFAULT_SIZES = (100, 500, 1000, 2000, 5000)
WARMUP_SIZE = 100
VALID_OPERATIONS = ("create", "update", "delete")
SUCCESS_CODES = {
    "create": (201,),
    "update": (200,),
    "delete": (200, 204),
}


def local_timestamp() -> str:
    """Local time with UTC offset, for matching monitoring samples."""
    return datetime.now().astimezone().isoformat(timespec="milliseconds")


class PerformanceRunner:
    """Run repeatable Todo API performance experiments."""

    def __init__(self, base_url: str, timeout: float = 10.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.run_id = uuid.uuid4().hex[:10]

    def close(self) -> None:
        self.session.close()

    def _request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        return self.session.request(
            method,
            f"{self.base_url}{path}",
            timeout=self.timeout,
            **kwargs,
        )

    def check_service(self) -> None:
        """Fail early if the Todo Manager API is unavailable."""
        try:
            response = self._request("GET", "/todos")
            response.raise_for_status()
        except requests.RequestException as error:
            raise RuntimeError(
                f"Todo Manager API is unavailable at {self.base_url}: {error}"
            ) from error

    @staticmethod
    def random_todo(index: int, run_id: str) -> dict[str, Any]:
        """Generate a valid Todo payload with unique identifying data."""
        suffix = "".join(
            random.choices(string.ascii_letters + string.digits, k=8)
        )
        return {
            "title": f"PartC-{run_id}-{index}-{suffix}",
            "description": (
                f"Generated performance-test record {index}; "
                f"random token {suffix}"
            ),
        }

    def create_objects(
        self, count: int, payloads: list[dict[str, Any]]
    ) -> tuple[list[int], list[str]]:
        """Create objects outside the timed region for UPDATE/DELETE."""
        created_ids: list[int] = []
        errors: list[str] = []

        for index, payload in enumerate(payloads):
            try:
                response = self._request("POST", "/todos", json=payload)
                if response.status_code not in SUCCESS_CODES["create"]:
                    errors.append(
                        f"setup create #{index}: HTTP {response.status_code} "
                        f"{response.text[:200]}"
                    )
                    continue

                body = response.json()
                todo_id = body.get("id")
                if todo_id is None:
                    errors.append(f"setup create #{index}: response has no id")
                    continue

                created_ids.append(int(todo_id))
            except (requests.RequestException, ValueError, TypeError) as error:
                errors.append(f"setup create #{index}: {error}")

        if errors:
            self.cleanup(created_ids)
            raise RuntimeError(
                f"Could not prepare {count} Todos; created "
                f"{len(created_ids)}. First errors: {'; '.join(errors[:3])}"
            )

        return created_ids, errors

    def cleanup(self, todo_ids: list[int]) -> list[str]:
        """Best-effort cleanup; cleanup time is never included in results."""
        errors: list[str] = []
        for todo_id in reversed(todo_ids):
            try:
                response = self._request("DELETE", f"/todos/{todo_id}")
                if response.status_code not in SUCCESS_CODES["delete"] + (404,):
                    errors.append(
                        f"cleanup Todo {todo_id}: HTTP {response.status_code}"
                    )
            except requests.RequestException as error:
                errors.append(f"cleanup Todo {todo_id}: {error}")
        return errors

    def measure_create(
        self, count: int, payloads: list[dict[str, Any]]
    ) -> tuple[dict[str, Any], list[int]]:
        created_ids: list[int] = []
        errors: list[str] = []
        phase_start = local_timestamp()
        started = time.perf_counter()

        for index, payload in enumerate(payloads):
            try:
                response = self._request("POST", "/todos", json=payload)
                if response.status_code not in SUCCESS_CODES["create"]:
                    errors.append(
                        f"create #{index}: HTTP {response.status_code} "
                        f"{response.text[:200]}"
                    )
                    continue

                todo_id = response.json().get("id")
                if todo_id is None:
                    errors.append(f"create #{index}: response has no id")
                    continue
                created_ids.append(int(todo_id))
            except (requests.RequestException, ValueError, TypeError) as error:
                errors.append(f"create #{index}: {error}")

        elapsed = time.perf_counter() - started
        phase = (phase_start, local_timestamp())
        return self.result_row(
            "create", phase, count, elapsed, len(created_ids), errors
        ), created_ids

    def measure_update(
        self, count: int, todo_ids: list[int], payloads: list[dict[str, Any]]
    ) -> dict[str, Any]:
        errors: list[str] = []
        phase_start = local_timestamp()
        started = time.perf_counter()

        for index, (todo_id, payload) in enumerate(zip(todo_ids, payloads)):
            update_payload = {
                "title": f"{payload['title']}-updated",
                "description": f"{payload['description']} [updated]",
            }
            try:
                # The existing Part A/Part B tests use POST for Todo updates.
                response = self._request(
                    "POST", f"/todos/{todo_id}", json=update_payload
                )
                if response.status_code not in SUCCESS_CODES["update"]:
                    errors.append(
                        f"update Todo {todo_id}: HTTP {response.status_code} "
                        f"{response.text[:200]}"
                    )
            except requests.RequestException as error:
                errors.append(f"update Todo {todo_id}: {error}")

        elapsed = time.perf_counter() - started
        phase = (phase_start, local_timestamp())
        successful = count - len(errors)
        return self.result_row("update", phase, count, elapsed, successful, errors)

    def measure_delete(self, count: int, todo_ids: list[int]) -> dict[str, Any]:
        errors: list[str] = []
        deleted_ids: set[int] = set()
        phase_start = local_timestamp()
        started = time.perf_counter()

        for todo_id in todo_ids:
            try:
                response = self._request("DELETE", f"/todos/{todo_id}")
                if response.status_code in SUCCESS_CODES["delete"]:
                    deleted_ids.add(todo_id)
                else:
                    errors.append(
                        f"delete Todo {todo_id}: HTTP {response.status_code} "
                        f"{response.text[:200]}"
                    )
            except requests.RequestException as error:
                errors.append(f"delete Todo {todo_id}: {error}")

        elapsed = time.perf_counter() - started
        phase = (phase_start, local_timestamp())
        return self.result_row("delete", phase, count, elapsed, len(deleted_ids), errors)

    def result_row(
        self,
        operation: str,
        phase: tuple[str, str],
        requested: int,
        elapsed: float,
        successful: int,
        errors: list[str],
    ) -> dict[str, Any]:
        return {
            "phase_start": phase[0],
            "phase_end": phase[1],
            "run_id": self.run_id,
            "operation": operation,
            "object_count": requested,
            "successful_operations": successful,
            "failed_operations": len(errors),
            "total_time_seconds": round(elapsed, 6),
            "average_time_ms_per_requested_object": round(
                elapsed * 1000 / requested, 6
            ) if requested else 0,
            "operations_per_second": round(
                successful / elapsed, 3
            ) if elapsed > 0 else 0,
            "error_details": " | ".join(errors[:5]),
        }

    def run_experiment(
        self, operation: str, count: int, repeat: int
    ) -> dict[str, Any]:
        payloads = [
            self.random_todo(index, f"{self.run_id}-{repeat}")
            for index in range(count)
        ]

        if operation == "create":
            row, created_ids = self.measure_create(count, payloads)
            cleanup_errors = self.cleanup(created_ids)
        else:
            todo_ids, _ = self.create_objects(count, payloads)
            try:
                if operation == "update":
                    row = self.measure_update(count, todo_ids, payloads)
                else:
                    row = self.measure_delete(count, todo_ids)
            finally:
                # For DELETE, this retries only objects not deleted successfully.
                cleanup_errors = self.cleanup(todo_ids)

        row["repeat"] = repeat
        row["cleanup_errors"] = len(cleanup_errors)
        if cleanup_errors:
            row["cleanup_details"] = " | ".join(cleanup_errors[:5])
        else:
            row["cleanup_details"] = ""
        return row


def parse_sizes(value: str) -> tuple[int, ...]:
    try:
        sizes = tuple(int(part.strip()) for part in value.split(","))
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            "Sizes must be comma-separated positive integers"
        ) from error

    if not sizes or any(size <= 0 for size in sizes):
        raise argparse.ArgumentTypeError("All sizes must be positive integers")
    return sizes


def parse_operations(value: str) -> tuple[str, ...]:
    operations = tuple(part.strip().lower() for part in value.split(","))
    invalid = set(operations) - set(VALID_OPERATIONS)
    if not operations or invalid:
        raise argparse.ArgumentTypeError(
            f"Operations must be selected from: {', '.join(VALID_OPERATIONS)}"
        )
    return operations


def write_results(rows: list[dict[str, Any]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())
    with output.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Measure Todo Manager REST API CREATE/UPDATE/DELETE performance."
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"API base URL (default: {DEFAULT_BASE_URL})",
    )
    parser.add_argument(
        "--sizes",
        type=parse_sizes,
        default=DEFAULT_SIZES,
        help="Comma-separated workload sizes (default: 100,500,1000,2000,5000)",
    )
    parser.add_argument(
        "--repeats",
        type=int,
        default=3,
        help="Number of repetitions per operation and workload (default: 3)",
    )
    parser.add_argument(
        "--operations",
        type=parse_operations,
        default=VALID_OPERATIONS,
        help="Comma-separated operations: create,update,delete",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("part_c/results/performance_results.csv"),
        help="CSV output path",
    )
    parser.add_argument("--seed", type=int, default=429, help="Random data seed")
    parser.add_argument("--timeout", type=float, default=10.0)
    args = parser.parse_args()

    if args.repeats <= 0:
        parser.error("--repeats must be positive")

    if args.output.exists():
        parser.error(f"{args.output} already exists; choose another --output")

    random.seed(args.seed)
    runner = PerformanceRunner(args.base_url, args.timeout)
    rows: list[dict[str, Any]] = []

    try:
        runner.check_service()
        print(f"API: {args.base_url}")
        print(f"Workloads: {', '.join(map(str, args.sizes))}")
        print(f"Operations: {', '.join(args.operations)}")
        print(f"Repeats: {args.repeats}")
        print(f"Seed: {args.seed}")
        print("Timing covers each request loop; setup and cleanup are excluded.")

        print("Warm-up (results discarded)...")
        for operation in args.operations:
            runner.run_experiment(operation, WARMUP_SIZE, 0)

        for operation in args.operations:
            for size in args.sizes:
                for repeat in range(1, args.repeats + 1):
                    row = runner.run_experiment(operation, size, repeat)
                    rows.append(row)
                    write_results(rows, args.output)
                    print(
                        f"{operation.upper():6} | n={size:5} | "
                        f"repeat={repeat} | "
                        f"total={row['total_time_seconds']:.4f}s | "
                        f"avg={row['average_time_ms_per_requested_object']:.3f}ms | "
                        f"success={row['successful_operations']}/{size} | "
                        f"errors={row['failed_operations']}"
                    )
    except (RuntimeError, requests.RequestException) as error:
        print(f"ERROR: {error}")
        return 1
    finally:
        runner.close()

    print(f"\nResults saved to: {args.output.resolve()}")
    if any(row["failed_operations"] or row["cleanup_errors"] for row in rows):
        print("WARNING: some operations or cleanups failed; check the CSV.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())