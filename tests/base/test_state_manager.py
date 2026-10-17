
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
