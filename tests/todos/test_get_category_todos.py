import xml.etree.ElementTree as ET

import pytest


@pytest.mark.parametrize(
    "accept",
    ["application/json", "application/xml"],
)
@pytest.mark.parametrize(
    "linked",
    [
        pytest.param(False, id="empty"),
        pytest.param(True, id="linked"),
    ],
)
def test_get_category_todos(
    api,
    entity_factory,
    state_manager,
    system_snapshot,
    accept,
    linked,
):
    category = entity_factory("categories")
    todo = entity_factory("todos")

    endpoint = f"/categories/{category['id']}/todos"

    if linked:
        created = api.post(
            endpoint,
            data={"id": todo["id"]},
            headers={"Accept": "application/json"},
        )
        assert created.status_code == 201, created.text

        state_manager.track_relationship(
            "categories",
            category["id"],
            "todos",
            todo["id"],
        )

    before = system_snapshot()

    response = api.get(
        endpoint,
        headers={"Accept": accept},
    )

    assert response.status_code == 200, response.text
    assert system_snapshot() == before

    content_type = response.headers.get("Content-Type", "")
    assert content_type.split(";")[0].strip().lower() == accept

    expected = [todo] if linked else []

    if accept == "application/json":
        assert response.json()["todos"] == expected
    else:
        root = ET.fromstring(response.content)
        assert root.tag == "todos"

        todos = root.findall("todo")
        assert len(todos) == len(expected)

        if linked:
            for field, value in todo.items():
                assert todos[0].findtext(field, "") == value