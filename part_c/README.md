# Part C: Todo Performance Test Suite

Measures how long the Todo Manager REST API takes to create, update and delete Todos as the workload grows. The suite follows the request approach used in our Part A tests (a shared requests session, with POST for Todo updates), but has its own client and cleanup code.

## Test environment

| Item | Value |
|---|---|
| Operating system | Windows 11 Home China (10.0.26300) |
| CPU and RAM | CPU: AMD Ryzen 9 7945HX with Radeon Graphics; RAM: 15.2 GB usable |
| Java version | 21.0.4 LTS (Java HotSpot 64-Bit Server VM) |
| Python version | 3.13.1 |
| Application under test | runTodoManagerRestAPI-1.5.5.jar on localhost:4567 |

## Setup

Run all commands from the repository root.

1. Activate the virtual environment: `.\.venv\Scripts\Activate.ps1`
2. Install dependencies (the script needs `requests`): `pip install -r requirements.txt`
3. In a separate terminal, start the server: `java -jar runTodoManagerRestAPI-1.5.5.jar`

The JAR must be in the folder where you run the command. Restart the server before each full run, and after any interrupted or failed run.

## Run

Final experiment (start CPU and memory monitoring first):

```powershell
python -m part_c.performance_test --sizes 100,500,1000,2000,5000,10000,20000 --repeats 5 --output part_c/results/final_run1.csv
```

Quick check:

```powershell
python -m part_c.performance_test --sizes 100,500 --repeats 1 --output part_c/results/trial.csv
```

| Option | Default | Meaning |
|---|---|---|
| `--base-url` | `http://localhost:4567` | Server address |
| `--sizes` | `100,500,1000,2000,5000` | Workload sizes |
| `--repeats` | `3` | Repetitions per operation and size |
| `--operations` | `create,update,delete` | Operations to test |
| `--output` | `part_c/results/performance_results.csv` | Result file; must not already exist |
| `--seed` | `429` | Seed for random data |
| `--timeout` | `10` | Request timeout in seconds |

## Method

- The script first checks that the service is available and stops if it is not.
- For each selected operation, a 100-object warm-up runs first and is not recorded.
- Operations run in the order given (by default create, update, delete). Each size is repeated before moving to the next.
- Object count is the number of operations in a phase. Create adds that many Todos to the starting data, update runs with that many added, and delete removes them progressively.
- Each timing uses `time.perf_counter()` around a sequential loop of requests. It includes client-side status checks and error handling. Create also includes reading the returned ID, and update includes building the update payload.
- Initial data generation, setup for update and delete, and cleanup are excluded from timing.
- Average time is total loop time divided by the requested object count, so check failure counts before comparing results.

## Test data

Each Todo has a title containing the run ID, repeat number, index and an 8-character random suffix, plus a description containing the index and suffix. With the same sizes, operations and repeat count, the seed reproduces the suffixes. Run IDs differ between runs.

## Success checks and cleanup

| Operation | Request | Expected status |
|---|---|---|
| Create | `POST /todos` | 201 |
| Update | `POST /todos/{id}` | 200 |
| Delete | `DELETE /todos/{id}` | 200 or 204 |

After each experiment, the script tries to delete the Todos whose IDs it recorded. A 404 during cleanup is accepted because the Todo is already gone. If operations or cleanups fail in a completed run, the script prints a warning and exits with code 1.

## Output

The CSV is saved after each experiment, with one row per operation, size and repeat. A full final run has 105 rows.

| Column | Meaning |
|---|---|
| `phase_start`, `phase_end` | Local time with UTC offset, for matching monitoring samples |
| `run_id` | Identifier for the script run |
| `operation` | create, update or delete |
| `object_count` | Requested number of operations |
| `successful_operations`, `failed_operations` | Outcome counts |
| `total_time_seconds` | Duration of the timed loop |
| `average_time_ms_per_requested_object` | Total time divided by object count, in ms |
| `operations_per_second` | Successful operations divided by total time |
| `error_details` | Up to five errors |
| `repeat` | Repetition number |
| `cleanup_errors`, `cleanup_details` | Cleanup error count and up to five details |

## Known limitations

- The client and server share one computer, so they compete for CPU and memory.
- Requests are sent one at a time, so concurrent load is not tested.
- Only per-phase totals and averages are recorded, not individual request latencies.
- Phases shorter than the monitoring interval may have no CPU or memory samples. Treat these as insufficient data, not zero.
- The server is not restarted between experiments, so earlier experiments may affect later ones.
- If a run is interrupted, or the server creates a Todo without the script receiving its ID, test data may remain. Restart the server.
