
import uuid

import pytest

from base.state_manager import StateManager


def test_cleanup_runs_after_failure(api):
    """Verify restoration runs even when a test operation fails."""

    title = f"Failure-Cleanup-{uuid.uuid4().hex[:8]}"
    manager = StateManager(api)
    todo_id = None

    try:
        response = api.post(
            "/todos",
            data={"title": title}
        )
        assert response.status_code == 201, response.text

        todo_id = response.json()["id"]
        manager.track_created("todos", todo_id)

        # Simulate an assertion failure.
        with pytest.raises(AssertionError):
            assert False, "Simulated test failure"

    finally:
        manager.restore()

    # Confirm cleanup removed the Todo.
    deleted = api.get(f"/todos/{todo_id}")

    assert deleted.status_code in (200, 404)

    if deleted.status_code == 200:
        assert deleted.json().get("todos", []) == []
