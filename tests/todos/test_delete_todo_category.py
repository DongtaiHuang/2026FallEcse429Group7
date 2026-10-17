import xml.etree.ElementTree as ET

import pytest


@pytest.mark.parametrize(
    "accept",
    ["application/json", "application/xml"],
)
@pytest.mark.parametrize(
    "case",
    [
        "linked",
        "unlinked",
        "missing-todo",
        "missing-category",
    ],
)
def test_delete_todo_category(
    api,
    entity_factory,
    state_manager,
    system_snapshot,
    accept,
    case,
):
    todo = entity_factory("todos")
    category = entity_factory("categories")

    todo_id = todo["id"]
    category_id = category["id"]
    collection = f"/todos/{todo_id}/categories"
    endpoint = f"{collection}/{category_id}"

    if case == "linked":
        created = api.post(
            collection,
            data={"id": category_id},
            headers={"Accept": "application/json"},
        )
        assert created.status_code == 201, created.text

        state_manager.track_relationship(
            "todos", todo_id, "categories", category_id
        )

    elif case == "missing-todo":
        deleted = api.delete(f"/todos/{todo_id}")
        assert deleted.status_code == 200, deleted.text

    elif case == "missing-category":
        deleted = api.delete(f"/categories/{category_id}")
        assert deleted.status_code == 200, deleted.text

    before = system_snapshot()

    response = api.delete(
        endpoint,
        headers={"Accept": accept},
    )

    if case == "linked":
        assert response.status_code == 200, response.text
        assert response.content == b""

        # Removing the link should restore the original Todo.
        before["todos"][todo_id] = todo

        verification = api.get(
            collection,
            headers={"Accept": "application/json"},
        )
        assert verification.status_code == 200
        assert verification.json()["categories"] == []

    else:
        assert response.status_code == 404, response.text

        if accept == "application/json":
            errors = response.json()["errorMessages"]
        else:
            root = ET.fromstring(response.content)
            assert root.tag == "errorMessages"
            errors = [
                element.text
                for element in root.findall("errorMessage")
            ]

        assert errors
        assert all(
            isinstance(message, str) and message.strip()
            for message in errors
        )

    # Both entities survive a successful relationship deletion.
    # Failed deletions must leave the entire state unchanged.
    assert system_snapshot() == before