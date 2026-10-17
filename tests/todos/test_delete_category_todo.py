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
        "missing-category",
        "missing-todo",
    ],
)
def test_delete_category_todo(
    api,
    entity_factory,
    state_manager,
    system_snapshot,
    accept,
    case,
):
    category = entity_factory("categories")
    todo = entity_factory("todos")

    category_id = category["id"]
    todo_id = todo["id"]
    collection = f"/categories/{category_id}/todos"
    endpoint = f"{collection}/{todo_id}"

    if case == "linked":
        created = api.post(
            collection,
            data={"id": todo_id},
            headers={"Accept": "application/json"},
        )
        assert created.status_code == 201, created.text

        state_manager.track_relationship(
            "categories", category_id, "todos", todo_id
        )

    elif case == "missing-category":
        deleted = api.delete(f"/categories/{category_id}")
        assert deleted.status_code == 200, deleted.text

    elif case == "missing-todo":
        deleted = api.delete(f"/todos/{todo_id}")
        assert deleted.status_code == 200, deleted.text

    before = system_snapshot()

    response = api.delete(
        endpoint,
        headers={"Accept": accept},
    )

    if case == "linked":
        assert response.status_code == 200, response.text
        assert response.content == b""

        # Removing the link should restore the original Category.
        before["categories"][category_id] = category

        verification = api.get(
            collection,
            headers={"Accept": "application/json"},
        )
        assert verification.status_code == 200
        assert verification.json()["todos"] == []

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

    assert system_snapshot() == before