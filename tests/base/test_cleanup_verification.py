
import uuid


def test_cleanup_verification(api, created_objects):
    """Verify that a Todo can be created and deleted."""

    title = f"ECSE429-cleanup-{uuid.uuid4().hex[:8]}"

    response = api.post(
        "/todos",
        data={"title": title}
    )

    assert response.status_code == 201, response.text

    todo_id = response.json()["id"]

    created_objects("todos", todo_id)

    # Confirm the Todo exists.
    get_response = api.get(f"/todos/{todo_id}")
    assert get_response.status_code == 200

    # Delete the Todo.
    delete_response = api.delete(f"/todos/{todo_id}")
    assert delete_response.status_code in (200, 204)

    # Confirm that the deleted Todo is no longer retrievable.
    verify_response = api.get(f"/todos/{todo_id}")

    assert verify_response.status_code in (404, 200)

    if verify_response.status_code == 200:
        assert not verify_response.json().get("todos")
