import pytest


@pytest.mark.parametrize(
    "accept",
    ["application/json", "application/xml"],
)
def test_post_category_todo_json(
    api,
    entity_factory,
    state_manager,
    system_snapshot,
    accept,
):
    category = entity_factory("categories")
    todo = entity_factory("todos")

    category_id = category["id"]
    todo_id = todo["id"]
    endpoint = f"/categories/{category_id}/todos"

    before = system_snapshot()

    response = api.post(
        endpoint,
        data={"id": todo_id},
        headers={"Accept": accept},
    )
    assert response.status_code == 201, response.text

    state_manager.track_relationship(
        "categories",
        category_id,
        "todos",
        todo_id,
    )

    assert response.content == b""

    # Only the Category's todos relationship should change.
    before["categories"][category_id]["todos"] = [
        {"id": todo_id}
    ]
    assert system_snapshot() == before

    verification = api.get(
        endpoint,
        headers={"Accept": "application/json"},
    )
    assert verification.status_code == 200, verification.text
    assert verification.json()["todos"] == [todo]


@pytest.mark.parametrize(
    "missing_type",
    [
        pytest.param("categories", id="missing-category"),
        pytest.param("todos", id="missing-todo"),
    ],
)
def test_post_category_todo_rejects_missing_entity(
    api,
    entity_factory,
    system_snapshot,
    missing_type,
):
    category = entity_factory("categories")
    todo = entity_factory("todos")

    entities = {
        "categories": category,
        "todos": todo,
    }
    missing_id = entities[missing_type]["id"]

    deleted = api.delete(f"/{missing_type}/{missing_id}")
    assert deleted.status_code == 200, deleted.text

    before = system_snapshot()

    response = api.post(
        f"/categories/{category['id']}/todos",
        data={"id": todo["id"]},
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