from uuid import uuid4
import xml.etree.ElementTree as ET

import pytest


@pytest.mark.parametrize(
    "content_type",
    ["application/json", "application/xml"],
)
@pytest.mark.parametrize(
    "changes",
    [
        pytest.param(
            {"doneStatus": True},
            id="update-status",
        ),
        pytest.param(
            {"title": "Updated Todo title"},
            id="update-title",
        ),
    ],
)
def test_post_todo_updates_only_supplied_fields(
    api,
    api_client,
    api_url,
    state_manager,
    system_snapshot,
    content_type,
    changes,
):
    response = api.post(
        "/todos",
        data={
            "title": f"pytest-amend-{uuid4().hex}",
            "doneStatus": False,
            "description": "Preserve this description",
        },
        headers={"Accept": "application/json"},
    )
    assert response.status_code == 201, response.text

    original = response.json()
    todo_id = original["id"]
    state_manager.track_created("todos", todo_id)

    before = system_snapshot()

    if content_type == "application/json":
        body_args = {"json": changes}
    else:
        root = ET.Element("todo")

        for field, value in changes.items():
            text = (
                str(value).lower()
                if isinstance(value, bool)
                else str(value)
            )
            ET.SubElement(root, field).text = text

        body_args = {
            "data": ET.tostring(root, encoding="utf-8")
        }

    response = api_client.post(
        f"{api_url}/todos/{todo_id}",
        headers={
            "Content-Type": content_type,
            "Accept": "application/json",
        },
        timeout=5,
        **body_args,
    )

    assert response.status_code == 200, response.text

    expected = original.copy()

    for field, value in changes.items():
        expected[field] = (
            str(value).lower()
            if isinstance(value, bool)
            else value
        )

    assert response.json() == expected

    # Only the selected Todo should change.
    before["todos"][todo_id] = expected
    assert system_snapshot() == before














@pytest.mark.parametrize(
    "content_type",
    ["application/json", "application/xml"],
)
@pytest.mark.parametrize(
    "case, payload, expected_status",
    [
        pytest.param(
            "invalid",
            {"title": ""},
            400,
            id="empty-title",
        ),
        pytest.param(
            "invalid",
            {"doneStatus": "invalid"},
            400,
            id="invalid-done-status",
        ),
        pytest.param(
            "missing",
            {"title": "Update a missing Todo"},
            404,
            id="missing-id",
        ),
    ],
)
def test_post_todo_rejects_invalid_update(
    api,
    api_client,
    api_url,
    state_manager,
    system_snapshot,
    content_type,
    case,
    payload,
    expected_status,
):
    created = api.post(
        "/todos",
        data={
            "title": f"pytest-invalid-amend-{uuid4().hex}",
            "doneStatus": False,
            "description": "Must remain unchanged",
        },
        headers={"Accept": "application/json"},
    )
    assert created.status_code == 201, created.text

    todo_id = created.json()["id"]
    state_manager.track_created("todos", todo_id)
    endpoint = f"/todos/{todo_id}"

    if case == "missing":
        deleted = api.delete(endpoint)
        assert deleted.status_code == 200, deleted.text

    before = system_snapshot()

    if content_type == "application/json":
        body_args = {"json": payload}
    else:
        root = ET.Element("todo")

        for field, value in payload.items():
            ET.SubElement(root, field).text = value

        body_args = {
            "data": ET.tostring(root, encoding="utf-8")
        }

    response = api_client.post(
        f"{api_url}{endpoint}",
        headers={
            "Content-Type": content_type,
            "Accept": "application/json",
        },
        timeout=5,
        **body_args,
    )

    assert response.status_code == expected_status, response.text

    errors = response.json()["errorMessages"]
    assert isinstance(errors, list)
    assert errors
    assert all(
        isinstance(message, str) and message.strip()
        for message in errors
    )

    assert system_snapshot() == before