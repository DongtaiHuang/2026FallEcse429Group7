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
def test_get_todo_categories(
    api,
    entity_factory,
    state_manager,
    system_snapshot,
    accept,
    linked,
):
    todo = entity_factory("todos")
    category = entity_factory("categories")

    endpoint = f"/todos/{todo['id']}/categories"

    if linked:
        created = api.post(
            endpoint,
            data={"id": category["id"]},
            headers={"Accept": "application/json"},
        )
        assert created.status_code == 201, created.text

        state_manager.track_relationship(
            "todos",
            todo["id"],
            "categories",
            category["id"],
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

    expected = [category] if linked else []

    if accept == "application/json":
        assert response.json()["categories"] == expected
    else:
        root = ET.fromstring(response.content)
        assert root.tag == "categories"

        categories = root.findall("category")
        assert len(categories) == len(expected)

        if linked:
            for field, value in category.items():
                assert categories[0].findtext(field, "") == value