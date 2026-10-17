from collections import Counter
import xml.etree.ElementTree as ET

import pytest


@pytest.mark.parametrize(
    "accept",
    ["application/json", "application/xml"],
)
def test_undocumented_get_aggregates_todo_categories(
    api,
    entity_factory,
    state_manager,
    system_snapshot,
    accept,
):
    category = entity_factory("categories")
    category_id = category["id"]

    # Two independent Todos reference the same Category.
    for _ in range(2):
        todo = entity_factory("todos")

        created = api.post(
            f"/todos/{todo['id']}/categories",
            data={"id": category_id},
            headers={"Accept": "application/json"},
        )
        assert created.status_code == 201, created.text

        state_manager.track_relationship(
            "todos", todo["id"], "categories", category_id
        )

    before = system_snapshot()
    fields = ("id", "title", "description")
    expected = []

    for todo in before["todos"].values():
        for reference in todo.get("categories", []):
            linked_category = before["categories"][reference["id"]]
            expected.append(
                tuple(linked_category[field] for field in fields)
            )

    response = api.get(
        "/todos/categories",
        headers={"Accept": accept},
    )
    assert response.status_code == 200, response.text

    content_type = response.headers.get("Content-Type", "")
    assert content_type.split(";")[0].strip().lower() == accept

    if accept == "application/json":
        actual = [
            tuple(category[field] for field in fields)
            for category in response.json()["categories"]
        ]
    else:
        root = ET.fromstring(response.content)
        assert root.tag == "categories"

        actual = [
            tuple(category.findtext(field, "") for field in fields)
            for category in root.findall("category")
        ]

    # Compare contents and duplicate counts without relying on order.
    assert Counter(actual) == Counter(expected)
    assert sum(item[0] == category_id for item in actual) == 2

    assert system_snapshot() == before