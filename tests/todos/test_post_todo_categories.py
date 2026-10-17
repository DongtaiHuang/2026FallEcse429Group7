import pytest


@pytest.mark.parametrize(
    "accept",
    ["application/json", "application/xml"],
)
def test_post_todo_category_json(
    api,
    entity_factory,
    state_manager,
    system_snapshot,
    accept,
):
    todo = entity_factory("todos")
    category = entity_factory("categories")

    todo_id = todo["id"]
    category_id = category["id"]
    endpoint = f"/todos/{todo_id}/categories"

    before = system_snapshot()

    response = api.post(
        endpoint,
        data={"id": category_id},
        headers={"Accept": accept},
    )
    assert response.status_code == 201, response.text

    state_manager.track_relationship(
        "todos",
        todo_id,
        "categories",
        category_id,
    )

    assert response.content == b""

    # Only the Todo's categories relationship should change.
    before["todos"][todo_id]["categories"] = [
        {"id": category_id}
    ]
    assert system_snapshot() == before

    # Verify that the new relationship can be queried.
    verification = api.get(
        endpoint,
        headers={"Accept": "application/json"},
    )
    assert verification.status_code == 200, verification.text
    assert verification.json()["categories"] == [category]














@pytest.mark.parametrize(
    "missing_type",
    [
        pytest.param("todos", id="missing-todo"),
        pytest.param("categories", id="missing-category"),
    ],
)
def test_post_todo_category_rejects_missing_entity(
    api,
    entity_factory,
    system_snapshot,
    missing_type,
):
    todo = entity_factory("todos")
    category = entity_factory("categories")

    entities = {
        "todos": todo,
        "categories": category,
    }
    missing_id = entities[missing_type]["id"]

    # Delete our temporary entity to obtain a known missing ID.
    deleted = api.delete(f"/{missing_type}/{missing_id}")
    assert deleted.status_code == 200, deleted.text

    before = system_snapshot()

    response = api.post(
        f"/todos/{todo['id']}/categories",
        data={"id": category["id"]},
        headers={"Accept": "application/json"},
    )

    assert response.status_code == 404, response.text

    errors = response.json()["errorMessages"]
    assert isinstance(errors, list)
    assert errors
    assert all(
        isinstance(message, str) and message.strip()
        for message in errors
    )

    assert system_snapshot() == before