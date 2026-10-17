from uuid import uuid4
import xml.etree.ElementTree as ET

import pytest


@pytest.fixture
def todo_record(api, state_manager):
    payload = {
        "title": f"pytest-get-by-id-{uuid4().hex}",
        "doneStatus": False,
        "description": "GET by ID test",
    }

    response = api.post(
        "/todos",
        data=payload,
        headers={"Accept": "application/json"},
    )
    assert response.status_code == 201, response.text

    created = response.json()
    state_manager.track_created("todos", created["id"])

    return created


@pytest.mark.parametrize(
    "accept",
    ["application/json", "application/xml"],
)
def test_get_existing_todo(
    api, todo_record, system_snapshot, accept
):
    before = system_snapshot()

    response = api.get(
        f"/todos/{todo_record['id']}",
        headers={"Accept": accept},
    )

    assert response.status_code == 200, response.text
    assert system_snapshot() == before

    content_type = response.headers.get("Content-Type", "")
    assert content_type.split(";")[0].strip().lower() == accept

    if accept == "application/json":
        assert response.json()["todos"] == [todo_record]
    else:
        root = ET.fromstring(response.content)
        assert root.tag == "todos"

        todos = root.findall("todo")
        assert len(todos) == 1

        for field, expected in todo_record.items():
            assert todos[0].findtext(field, "") == expected


@pytest.mark.parametrize(
    "accept",
    ["application/json", "application/xml"],
)
def test_get_missing_todo(
    api, todo_record, system_snapshot, accept
):
    endpoint = f"/todos/{todo_record['id']}"

    # Delete our temporary Todo to obtain a known missing ID.
    deleted = api.delete(endpoint)
    assert deleted.status_code == 200, deleted.text

    before = system_snapshot()

    response = api.get(
        endpoint,
        headers={"Accept": accept},
    )

    assert response.status_code == 404, response.text
    assert system_snapshot() == before

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