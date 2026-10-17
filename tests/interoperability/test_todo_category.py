
import uuid


def test_create_todo_and_category(api, created_objects):
    """Check that a Todo and Category can coexist."""

    suffix = uuid.uuid4().hex[:8]

    todo_response = api.post(
        "/todos",
        data={"title": f"Interop-Todo-{suffix}"}
    )
    assert todo_response.status_code == 201, todo_response.text

    todo_id = todo_response.json()["id"]
    created_objects("todos", todo_id)

    category_response = api.post(
        "/categories",
        data={"title": f"Interop-Category-{suffix}"}
    )
    assert category_response.status_code == 201, category_response.text

    category_id = category_response.json()["id"]
    created_objects("categories", category_id)

    # Confirm that both objects can be retrieved.
    todo_get = api.get(f"/todos/{todo_id}")
    category_get = api.get(f"/categories/{category_id}")

    assert todo_get.status_code == 200
    assert category_get.status_code == 200

    print(f"\nCreated Todo ID: {todo_id}")
    print(f"Created Category ID: {category_id}")
    print(f"Todo response: {todo_get.json()}")
    print(f"Category response: {category_get.json()}")

def test_link_todo_to_category(api, created_objects):
    """Explore linking a Todo to a Category."""
    import uuid

    suffix = uuid.uuid4().hex[:8]

    # Create Todo
    todo_response = api.post(
        "/todos",
        data={"title": f"Linked-Todo-{suffix}"}
    )
    assert todo_response.status_code == 201

    todo_id = todo_response.json()["id"]
    created_objects("todos", todo_id)

    # Create Category
    category_response = api.post(
        "/categories",
        data={"title": f"Linked-Category-{suffix}"}
    )
    assert category_response.status_code == 201

    category_id = category_response.json()["id"]
    created_objects("categories", category_id)

    # Link the Todo to the Category
    link_response = api.post(
        f"/todos/{todo_id}/categories",
        data={"id": category_id}
    )

    print("\nLink status:", link_response.status_code)
    print("Link response:", link_response.text)

    # Retrieve the Todo's categories
    categories_response = api.get(
        f"/todos/{todo_id}/categories"
    )

    print("Categories status:", categories_response.status_code)
    print("Categories response:", categories_response.text)

def test_delete_todo_preserves_category(api, created_objects):
    """Explore what happens when a linked Todo is deleted."""
    import uuid

    suffix = uuid.uuid4().hex[:8]

    # Create Todo
    todo_response = api.post(
        "/todos",
        data={"title": f"Delete-Todo-{suffix}"}
    )
    assert todo_response.status_code == 201
    todo_id = todo_response.json()["id"]
    created_objects("todos", todo_id)

    # Create Category
    category_response = api.post(
        "/categories",
        data={"title": f"Keep-Category-{suffix}"}
    )
    assert category_response.status_code == 201
    category_id = category_response.json()["id"]
    created_objects("categories", category_id)

    # Link the Todo and Category
    link_response = api.post(
        f"/todos/{todo_id}/categories",
        data={"id": category_id}
    )
    assert link_response.status_code == 201

    # Delete the Todo
    delete_response = api.delete(f"/todos/{todo_id}")
    print("\nDelete Todo status:", delete_response.status_code)

    # Check whether the Category still exists
    category_get = api.get(f"/categories/{category_id}")
    print("Category after Todo deletion:", category_get.text)

    # Check whether the relationship remains
    relationship_get = api.get(
        f"/categories/{category_id}/todos"
    )
    print("Relationships after deletion:", relationship_get.text)

    # Verify the Category still exists
    assert category_get.status_code == 200
    categories = category_get.json()["categories"]
    assert len(categories) == 1
    assert categories[0]["id"] == str(category_id)

    # Verify the deleted Todo is no longer linked.
    assert relationship_get.status_code == 200

    linked_todos = relationship_get.json()["todos"]

    assert linked_todos == [], (
        "Deleted Todo is still linked to the Category"
    )

    # Verify the deleted Todo cannot be retrieved.
    deleted_todo = api.get(f"/todos/{todo_id}")

    assert deleted_todo.status_code in (200, 404)

    if deleted_todo.status_code == 200:
        assert deleted_todo.json().get("todos", []) == []
