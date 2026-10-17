import xml.etree.ElementTree as ET


from uuid import uuid4

import pytest


@pytest.mark.parametrize("done_status", [False, True])
def test_create_todo_json(api, state_manager, done_status):
    payload = {
        "title": f"pytest-create-{uuid4().hex}",
        "doneStatus": done_status,
        "description": "Todo creation test"
    }

    response = api.post(
        "/todos",
        data=payload,
        headers={"Accept": "application/json"}
    )
    assert response.status_code == 201, response.text

    created = response.json()
    todo_id = created["id"]
    state_manager.track_created("todos", todo_id)

    assert todo_id
    assert created["title"] == payload["title"]
    assert created["description"] == payload["description"]
    assert created["doneStatus"] == str(done_status).lower()

    response = api.get(
        f"/todos/{todo_id}",
        headers={"Accept": "application/json"}
    )
    assert response.status_code == 200, response.text

    todos = response.json()["todos"]
    assert len(todos) == 1
    assert todos[0] == created	










def test_create_todo_with_minimal_fields(api, state_manager):
    title = f"pytest-minimal-{uuid4().hex}"

    response = api.post(
        "/todos",
        data={"title": title},
        headers={"Accept": "application/json"}
    )
    assert response.status_code == 201, response.text

    created = response.json()
    todo_id = created["id"]
    state_manager.track_created("todos", todo_id)

    assert created["title"] == title
    assert created["doneStatus"] == "false"
    assert created["description"] == ""

    response = api.get(
        f"/todos/{todo_id}",
        headers={"Accept": "application/json"}
    )
    assert response.status_code == 200, response.text
    assert response.json()["todos"] == [created]


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param(
            {"description": "Missing title"},
            id="missing-title"
        ),
        pytest.param(
            {"title": ""},
            id="empty-title"
        ),
        pytest.param(
            {"title": "Invalid status", "doneStatus": "invalid"},
            id="invalid-done-status"
        )
    ]
)
def test_create_todo_rejects_invalid_fields(
    api, state_manager, payload
):
    response = api.post(
        "/todos",
        data=payload,
        headers={"Accept": "application/json"}
    )

    if response.status_code == 201:
        state_manager.track_created("todos", response.json()["id"])

    assert response.status_code == 400, response.text

    errors = response.json()["errorMessages"]
    assert isinstance(errors, list)
    assert errors
    assert all(isinstance(message, str) and message for message in errors)





@pytest.mark.parametrize("done_status", [False, True])
def test_create_todo_xml(
    api, api_client, api_url, state_manager, done_status
):
    title = f"pytest-xml-{uuid4().hex}"
    status_text = str(done_status).lower()

    xml_body = (
        "<todo>"
        f"<title>{title}</title>"
        f"<doneStatus>{status_text}</doneStatus>"
        "<description>XML creation test</description>"
        "</todo>"
    )

    response = api_client.post(
        f"{api_url}/todos",
        data=xml_body.encode("utf-8"),
        headers={
            "Content-Type": "application/xml",
            "Accept": "application/xml"
        },
        timeout=5
    )
    assert response.status_code == 201, response.text

    root = ET.fromstring(response.content)
    todo_id = root.findtext("id")
    assert todo_id
    state_manager.track_created("todos", todo_id)

    assert root.tag == "todo"
    assert root.findtext("title") == title
    assert root.findtext("doneStatus") == status_text
    assert root.findtext("description") == "XML creation test"

    response = api.get(
        f"/todos/{todo_id}",
        headers={"Accept": "application/json"}
    )
    assert response.status_code == 200, response.text
    assert response.json()["todos"] == [
        {
            "id": todo_id,
            "title": title,
            "doneStatus": status_text,
            "description": "XML creation test"
        }
    ]









@pytest.mark.parametrize(
    "content_type, body",
    [
        pytest.param(
            "application/json",
            '{"title": }',
            id="malformed-json"
        ),
        pytest.param(
            "application/xml",
            "<todo><title>Broken XML</todo>",
            id="malformed-xml"
        )
    ]
)
def test_create_todo_rejects_malformed_payload(
    api_client, api_url, state_manager, content_type, body
):
    response = api_client.post(
        f"{api_url}/todos",
        data=body.encode("utf-8"),
        headers={
            "Content-Type": content_type,
            "Accept": "application/json"
        },
        timeout=5
    )

    if response.status_code == 201:
        state_manager.track_created("todos", response.json()["id"])

    assert response.status_code == 400, response.text

    errors = response.json()["errorMessages"]
    assert isinstance(errors, list)
    assert errors
    assert all(isinstance(message, str) and message for message in errors)










@pytest.mark.parametrize(
    "content_type",
    ["application/json", "application/xml"]
)
def test_create_todo_changes_only_new_todo(
    api_client, api_url, state_manager,
    system_snapshot, content_type
):
    before = system_snapshot()
    title = f"pytest-side-effect-{uuid4().hex}"

    payload = {
        "title": title,
        "doneStatus": False,
        "description": "Creation side-effect check"
    }

    if content_type == "application/json":
        body_args = {"json": payload}
    else:
        root = ET.Element("todo")
        ET.SubElement(root, "title").text = title
        ET.SubElement(root, "doneStatus").text = "false"
        ET.SubElement(root, "description").text = payload["description"]
        body_args = {"data": ET.tostring(root, encoding="utf-8")}

    response = api_client.post(
        f"{api_url}/todos",
        headers={
            "Content-Type": content_type,
            "Accept": "application/json"
        },
        timeout=5,
        **body_args
    )
    assert response.status_code == 201, response.text

    created = response.json()
    todo_id = created["id"]
    state_manager.track_created("todos", todo_id)

    assert todo_id not in before["todos"]
    assert created == {
        "id": todo_id,
        "title": title,
        "doneStatus": "false",
        "description": payload["description"]
    }

    expected = before
    expected["todos"][todo_id] = created

    assert system_snapshot() == expected