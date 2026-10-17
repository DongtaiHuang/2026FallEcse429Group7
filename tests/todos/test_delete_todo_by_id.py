from uuid import uuid4
import xml.etree.ElementTree as ET

import pytest


@pytest.mark.parametrize(
    "accept",
    ["application/json", "application/xml"],
)
@pytest.mark.parametrize(
    "todo_exists",
    [
        pytest.param(True, id="existing"),
        pytest.param(False, id="missing"),
    ],
)
def test_delete_todo_by_id(
    api,
    state_manager,
    system_snapshot,
    accept,
    todo_exists,
):
    created = api.post(
        "/todos",
        data={"title": f"pytest-delete-{uuid4().hex}"},
        headers={"Accept": "application/json"},
    )
    assert created.status_code == 201, created.text

    todo_id = created.json()["id"]
    state_manager.track_created("todos", todo_id)
    endpoint = f"/todos/{todo_id}"

    if not todo_exists:
        deleted = api.delete(endpoint)
        assert deleted.status_code == 200, deleted.text

    before = system_snapshot()

    response = api.delete(
        endpoint,
        headers={"Accept": accept},
    )

    if todo_exists:
        assert response.status_code == 200, response.text
        assert response.content == b""

        # Only our temporary Todo should disappear.
        del before["todos"][todo_id]
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

    # Confirm that the Todo cannot be retrieved afterward.
    verification = api.get(
        endpoint,
        headers={"Accept": accept},
    )
    assert verification.status_code == 404, verification.text