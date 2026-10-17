from uuid import uuid4
import xml.etree.ElementTree as ET

import pytest


@pytest.mark.parametrize(
    "content_type",
    ["application/json", "application/xml"],
)
@pytest.mark.parametrize(
    "complete_payload",
    [
        pytest.param(True, id="replace-all-fields"),
        pytest.param(False, id="reset-omitted-fields"),
    ],
)
def test_put_todo_replaces_fields(
    api,
    api_client,
    api_url,
    state_manager,
    system_snapshot,
    content_type,
    complete_payload,
):
    created = api.post(
        "/todos",
        data={
            "title": f"pytest-put-{uuid4().hex}",
            "doneStatus": True,
            "description": "Original description",
        },
        headers={"Accept": "application/json"},
    )
    assert created.status_code == 201, created.text

    todo_id = created.json()["id"]
    state_manager.track_created("todos", todo_id)

    payload = {"title": f"replacement-{uuid4().hex}"}

    if complete_payload:
        payload["doneStatus"] = False
        payload["description"] = "Replacement description"

    before = system_snapshot()

    if content_type == "application/json":
        body_args = {"json": payload}
    else:
        root = ET.Element("todo")

        for field, value in payload.items():
            text = (
                str(value).lower()
                if isinstance(value, bool)
                else str(value)
            )
            ET.SubElement(root, field).text = text

        body_args = {
            "data": ET.tostring(root, encoding="utf-8")
        }

    response = api_client.put(
        f"{api_url}/todos/{todo_id}",
        headers={
            "Content-Type": content_type,
            "Accept": "application/json",
        },
        timeout=5,
        **body_args,
    )

    assert response.status_code == 200, response.text

    expected = {
        "id": todo_id,
        "title": payload["title"],
        "doneStatus": "false",
        "description": payload.get("description", ""),
    }

    assert response.json() == expected

    # Verify persistence and absence of unrelated changes.
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
            {"description": "Missing required title"},
            400,
            id="missing-title",
        ),
        pytest.param(
            "invalid",
            {"title": ""},
            400,
            id="empty-title",
        ),
        pytest.param(
            "invalid",
            {
                "title": "Invalid status test",
                "doneStatus": "invalid",
            },
            400,
            id="invalid-done-status",
        ),
        pytest.param(
            "missing",
            {"title": "Replace a missing Todo"},
            404,
            id="missing-id",
        ),
    ],
)
def test_put_todo_rejects_invalid_replacement(
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
            "title": f"pytest-invalid-put-{uuid4().hex}",
            "doneStatus": True,
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

    response = api_client.put(
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