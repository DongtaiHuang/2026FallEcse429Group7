
import uuid


def test_create_todo_with_cleanup(api, created_objects):
    """Create a todo and register it for automatic cleanup."""

    unique_title = f"ECSE429-test-{uuid.uuid4().hex[:8]}"

    response = api.post(
        "/todos",
        data={"title": unique_title}
    )

    assert response.status_code == 201, response.text

    todo = response.json()
    todo_id = todo["id"]

    # Register the todo for cleanup.
    created_objects("todos", todo_id)

    # Verify that the Todo exists.
    get_response = api.get(f"/todos/{todo_id}")

    assert get_response.status_code == 200

    # Inspect the actual API response.

    # Verify the Todo's title.
    todos = get_response.json()["todos"]

    assert len(todos) == 1
    assert todos[0]["id"] == str(todo_id)
    assert todos[0]["title"] == unique_title

