"""Invalid input: malformed JSON and XML bodies sent to the task-link POST endpoints.

Asserts what the app does today (400 and nothing created). The wrong Content-Type and the leaked Java
text of these error responses are covered by the bug 4 modules.
"""
import pytest

from task_link_support import JSON, XML, project_tasks_path, send_raw, todo_projects_path

MALFORMED_JSON_BODIES = {
    "closing brace missing": '{"id": "{id}"',
    "not json at all": "not json at all",
    "json array instead of object": '[{"id": "{id}"}]',
}


@pytest.mark.parametrize("body_template", MALFORMED_JSON_BODIES.values(), ids=MALFORMED_JSON_BODIES.keys())
def test_malformed_json_to_project_tasks_returns_400_and_links_nothing(api, create_project, create_todo, body_template):
    project_id, todo_id = create_project(), create_todo()

    response = send_raw(api, "POST", project_tasks_path(project_id), body=body_template.replace("{id}", todo_id), content_type=JSON)

    assert response.status_code == 400
    assert "errorMessages" in response.text
    assert api.get(project_tasks_path(project_id)).json() == {"todos": []}


@pytest.mark.parametrize("body_template", MALFORMED_JSON_BODIES.values(), ids=MALFORMED_JSON_BODIES.keys())
def test_malformed_json_to_todo_tasksof_returns_400_and_links_nothing(api, create_project, create_todo, body_template):
    project_id, todo_id = create_project(), create_todo()

    response = send_raw(api, "POST", todo_projects_path(todo_id), body=body_template.replace("{id}", project_id), content_type=JSON)

    assert response.status_code == 400
    assert api.get(todo_projects_path(todo_id)).json() == {"projects": []}


def test_malformed_xml_to_project_tasks_returns_400_and_links_nothing(api, create_project, create_todo):
    project_id, todo_id = create_project(), create_todo()

    response = send_raw(api, "POST", project_tasks_path(project_id), body=f"<todo><id>{todo_id}</id>", content_type=XML, accept=XML)

    assert response.status_code == 400
    assert "errorMessage" in response.text
    assert api.get(project_tasks_path(project_id)).json() == {"todos": []}


def test_malformed_xml_to_todo_tasksof_returns_400_and_links_nothing(api, create_project, create_todo):
    project_id, todo_id = create_project(), create_todo()

    response = send_raw(api, "POST", todo_projects_path(todo_id), body=f"<project><id>{project_id}</id>", content_type=XML, accept=XML)

    assert response.status_code == 400
    assert api.get(todo_projects_path(todo_id)).json() == {"projects": []}


def test_xml_body_declared_as_json_returns_400(api, create_project, create_todo):
    project_id, todo_id = create_project(), create_todo()

    response = send_raw(api, "POST", project_tasks_path(project_id), body=f"<todo><id>{todo_id}</id></todo>", content_type=JSON)

    assert response.status_code == 400
    assert api.get(project_tasks_path(project_id)).json() == {"todos": []}


def test_missing_body_returns_400_and_links_nothing(api, create_project):
    project_id = create_project()

    response = send_raw(api, "POST", project_tasks_path(project_id), body="", content_type=JSON)

    assert response.status_code == 400
    assert api.get(project_tasks_path(project_id)).json() == {"todos": []}


def test_content_type_is_not_enforced_for_json_bodies(api, create_project, create_todo, state):
    """Current behaviour: valid JSON sent as text/plain is accepted and creates the link."""
    project_id, todo_id = create_project(), create_todo()

    response = send_raw(api, "POST", project_tasks_path(project_id), body=f'{{"id": "{todo_id}"}}', content_type="text/plain")
    state.track_relationship("projects", project_id, "tasks", todo_id)

    assert response.status_code == 201
    assert [todo["id"] for todo in api.get(project_tasks_path(project_id)).json()["todos"]] == [todo_id]
