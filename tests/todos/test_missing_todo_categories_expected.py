import xml.etree.ElementTree as ET

import pytest


@pytest.mark.parametrize(
    "accept",
    ["application/json", "application/xml"],
)
def test_missing_todo_should_not_return_unrelated_categories(
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

    assert system_snapshot() == before
    assert response.status_code in (200, 404), response.text

    # An empty result or a not-found response exposes no unrelated data.
    if response.status_code == 200:
        if accept == "application/json":
            categories = response.json()["categories"]
        else:
            root = ET.fromstring(response.content)
            assert root.tag == "categories"
            categories = root.findall("category")

        assert categories == [], response.text