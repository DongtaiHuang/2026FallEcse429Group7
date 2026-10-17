import xml.etree.ElementTree as ET

import pytest


@pytest.mark.parametrize(
    "accept",
    ["application/json", "application/xml"],
)
def test_missing_todo_currently_returns_unrelated_category(
    api,
    missing_todo_category_probe,
    system_snapshot,
    accept,
):
    probe = missing_todo_category_probe
    before = system_snapshot()

    response = api.get(
        probe["endpoint"],
        headers={"Accept": accept},
    )

    assert response.status_code == 200, response.text

    if accept == "application/json":
        category_ids = [
            category["id"]
            for category in response.json()["categories"]
        ]
    else:
        root = ET.fromstring(response.content)
        assert root.tag == "categories"
        category_ids = [
            category.findtext("id")
            for category in root.findall("category")
        ]

    assert probe["category"]["id"] in category_ids
    assert system_snapshot() == before