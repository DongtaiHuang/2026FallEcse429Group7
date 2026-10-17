
import uuid

from base.state_manager import StateManager


def track_update(self, entity_type, entity_id):
        """Save an entity's current fields for later restoration."""
        if entity_type not in ("todos", "projects", "categories"):
            raise ValueError(f"Invalid entity type: {entity_type}")

        response = self.api.get(
            f"/{entity_type}/{entity_id}"
        )
        response.raise_for_status()

        entities = response.json()[entity_type]
        if len(entities) != 1:
            raise AssertionError("Expected exactly one entity")

        original = entities[0].copy()

        def undo():
            payload = {
                key: value
                for key, value in original.items()
                if key != "id"
            }

            result = self.api.put(
                f"/{entity_type}/{entity_id}",
                data=payload
            )

            if not 200 <= result.status_code < 300:
                raise AssertionError(
                    f"Could not restore {entity_type}/{entity_id}: "
                    f"HTTP {result.status_code}: {result.text}"
                )

        self.undo_actions.append(undo)

def test_state_manager_restores_created_todo(api):
    """Verify a newly created Todo is removed by StateManager."""

    title = f"StateManager-Test-{uuid.uuid4().hex[:8]}"

    response = api.post(
        "/todos",
        data={"title": title}
    )
    assert response.status_code == 201, response.text

    todo_id = response.json()["id"]

    manager = StateManager(api)
    manager.track_created("todos", todo_id)

    try:
        # Confirm that the Todo exists before restoration.
        get_response = api.get(f"/todos/{todo_id}")
        assert get_response.status_code == 200
        assert get_response.json()["todos"][0]["title"] == title
    finally:
        # Always restore, including when assertions fail.
        manager.restore()

    # Independently verify the Todo is gone.
    deleted_response = api.get(f"/todos/{todo_id}")

    assert deleted_response.status_code in (200, 404)

    if deleted_response.status_code == 200:
        assert deleted_response.json().get("todos", []) == []

def test_state_manager_restores_updated_todo(api):
    """Verify that StateManager restores a Todo's original title."""

    original_title = f"Original-{uuid.uuid4().hex[:8]}"
    updated_title = f"Updated-{uuid.uuid4().hex[:8]}"

    # Create a Todo
    response = api.post(
        "/todos",
        data={"title": original_title}
    )
    assert response.status_code == 201, response.text

    todo_id = response.json()["id"]

    manager = StateManager(api)
    

    try:
        # Save the original Todo before updating it.
        manager.track_update("todos", todo_id)
        print("Registered undo actions:", len(manager.undo_actions))
                # Modify the Todo.
        update_response = api.put(
            f"/todos/{todo_id}",
            data={"title": updated_title}
        )

        print("\nUpdate status:", update_response.status_code)
        print("Update response:", update_response.text)

        assert 200 <= update_response.status_code < 300

        # Verify the updated title.
        get_response = api.get(f"/todos/{todo_id}")
        assert get_response.status_code == 200

        assert get_response.json()["todos"][0]["title"] == updated_title
        print("Undo actions before restore:", len(manager.undo_actions))
        # Restore the original values.
        manager.restore()

        # Verify that the original title was restored.
        restored_response = api.get(f"/todos/{todo_id}")
        assert restored_response.status_code == 200

        assert (
            restored_response.json()["todos"][0]["title"]
            == original_title
        )

    finally:
        # Ensure the temporary Todo is deleted.
        api.delete(f"/todos/{todo_id}")

def test_state_manager_restores_relationship(api):
    """Verify cleanup removes a link but preserves both objects."""

    suffix = uuid.uuid4().hex[:8]

    manager = StateManager(api)
    todo_id = None
    category_id = None

    try:
        # Create a temporary Todo.
        todo_response = api.post(
            "/todos",
            data={"title": f"Relation-Todo-{suffix}"}
        )
        assert todo_response.status_code == 201, todo_response.text

        todo_id = todo_response.json()["id"]

        # Create a temporary Category.
        category_response = api.post(
            "/categories",
            data={"title": f"Relation-Category-{suffix}"}
        )
        assert category_response.status_code == 201, category_response.text

        category_id = category_response.json()["id"]

        # Link the Todo and Category.
        link_response = api.post(
            f"/todos/{todo_id}/categories",
            data={"id": category_id}
        )
        assert link_response.status_code == 201, link_response.text

        # Register the relationship for cleanup.
        manager.track_relationship(
            "todos",
            todo_id,
            "categories",
            category_id
        )

        # Confirm the relationship exists.
        before = api.get(f"/todos/{todo_id}/categories")
        assert before.status_code == 200
        assert any(
            str(category["id"]) == str(category_id)
            for category in before.json()["categories"]
        )

        # Restore the state by removing the relationship.
        manager.restore()

        # Verify the link has been removed.
        after = api.get(f"/todos/{todo_id}/categories")
        assert after.status_code == 200
        assert after.json()["categories"] == []

        # Verify that both entities still exist.
        todo_get = api.get(f"/todos/{todo_id}")
        category_get = api.get(f"/categories/{category_id}")

        assert todo_get.status_code == 200
        assert category_get.status_code == 200

        assert len(todo_get.json()["todos"]) == 1
        assert len(category_get.json()["categories"]) == 1

    finally:
        # Cleanup is attempted even if an assertion fails.
        try:
            manager.restore()
        finally:
            if todo_id is not None:
                api.delete(f"/todos/{todo_id}")
            if category_id is not None:
                api.delete(f"/categories/{category_id}")

def test_restore_deleted_relationship(api):
    """Verify a deleted Todo-Category link can be restored."""

    suffix = uuid.uuid4().hex[:8]
    manager = StateManager(api)

    todo_id = None
    category_id = None

    try:
        # Create a Todo.
        todo_response = api.post(
            "/todos",
            data={"title": f"Restore-Todo-{suffix}"}
        )
        assert todo_response.status_code == 201, todo_response.text
        todo_id = todo_response.json()["id"]

        # Create a Category.
        category_response = api.post(
            "/categories",
            data={"title": f"Restore-Category-{suffix}"}
        )
        assert category_response.status_code == 201, category_response.text
        category_id = category_response.json()["id"]

        # Create the original relationship.
        link_response = api.post(
            f"/todos/{todo_id}/categories",
            data={"id": category_id}
        )
        assert link_response.status_code == 201, link_response.text

        # Register the relationship for restoration.
        manager.track_deleted_relationship(
            "todos", todo_id, "categories", category_id
        )

        # Delete the relationship.
        delete_response = api.delete(
            f"/todos/{todo_id}/categories/{category_id}"
        )
        assert 200 <= delete_response.status_code < 300

        # Verify the relationship was removed.
        after_delete = api.get(
            f"/todos/{todo_id}/categories"
        )
        assert after_delete.status_code == 200
        assert after_delete.json()["categories"] == []

        # Restore the relationship.
        manager.restore()

        # Verify the relationship exists again.
        restored = api.get(
            f"/todos/{todo_id}/categories"
        )
        assert restored.status_code == 200

        assert any(
            str(category["id"]) == str(category_id)
            for category in restored.json()["categories"]
        )

    finally:
        # Cleanup temporary objects, even if the test fails.
        try:
            manager.restore()
        finally:
            if todo_id is not None:
                api.delete(f"/todos/{todo_id}")
            if category_id is not None:
                api.delete(f"/categories/{category_id}")
