import xml.etree.ElementTree as ET
import json
from uuid import uuid4



def test_get_todos_json(api):
    response = api.get(
        "/todos",
        headers={"Accept": "application/json"}
    )

    assert response.status_code == 200

    content_type = response.headers.get("Content-Type", "")
    assert content_type.split(";")[0].strip().lower() == "application/json"

    body = response.json()
    assert isinstance(body, dict)
    assert "todos" in body
    assert isinstance(body["todos"], list)






def test_get_todos_xml(api):
    response = api.get(
        "/todos",
        headers={"Accept": "application/xml"}
    )

    assert response.status_code == 200

    content_type = response.headers.get("Content-Type", "")
    assert content_type.split(";")[0].strip().lower() == "application/xml"

    root = ET.fromstring(response.content)
    assert root.tag == "todos"

    for todo in root:
        assert todo.tag == "todo"
        assert todo.findtext("id")
        assert todo.find("title") is not None
        assert todo.findtext("doneStatus") in ("true", "false")





def test_filter_todos_by_done_status(api, state_manager):
    todo_ids = {}

    for status in (True, False):
        response = api.post(
            "/todos",
            data={
                "title": f"pytest filter probe {status}",
                "doneStatus": status
            },
            headers={"Accept": "application/json"}
        )
        assert response.status_code == 201, response.text

        todo_id = response.json()["id"]
        state_manager.track_created("todos", todo_id)
        todo_ids[status] = todo_id

    for status in (True, False):
        expected_status = str(status).lower()

        response = api.get(
            "/todos",
            params={"doneStatus": expected_status},
            headers={"Accept": "application/json"}
        )
        assert response.status_code == 200, response.text

        todos = response.json()["todos"]
        returned_ids = {todo["id"] for todo in todos}

        assert todo_ids[status] in returned_ids
        assert todo_ids[not status] not in returned_ids
        assert all(
            todo["doneStatus"] == expected_status
            for todo in todos
        )
















def test_get_todos_has_no_side_effects(api):
    def normalize(value):
        if isinstance(value, dict):
            return {
                key: normalize(item)
                for key, item in value.items()
            }

        if isinstance(value, list):
            items = [normalize(item) for item in value]
            return sorted(
                items,
                key=lambda item: json.dumps(item, sort_keys=True)
            )

        return value

    def snapshot():
        state = {}

        for entity in ("todos", "categories", "projects"):
            response = api.get(
                f"/{entity}",
                headers={"Accept": "application/json"}
            )
            assert response.status_code == 200, response.text
            state[entity] = normalize(response.json())

        return state

    before = snapshot()

    for accept in ("application/json", "application/xml"):
        response = api.get(
            "/todos",
            headers={"Accept": accept}
        )
        assert response.status_code == 200, response.text
        assert snapshot() == before, (
            f"GET /todos with Accept={accept} changed system data"
        )















def test_filter_todos_by_title(api, state_manager):
    title = f"pytest-title-{uuid4().hex}"

    response = api.post(
        "/todos",
        data={"title": title},
        headers={"Accept": "application/json"}
    )
    assert response.status_code == 201, response.text

    todo_id = response.json()["id"]
    state_manager.track_created("todos", todo_id)

    response = api.get(
        "/todos",
        params={"title": title},
        headers={"Accept": "application/json"}
    )
    assert response.status_code == 200, response.text

    todos = response.json()["todos"]
    assert len(todos) == 1
    assert todos[0]["id"] == todo_id
    assert todos[0]["title"] == title

    response = api.get(
        "/todos",
        params={"title": f"{title}-missing"},
        headers={"Accept": "application/json"}
    )
    assert response.status_code == 200, response.text
    assert response.json()["todos"] == []

