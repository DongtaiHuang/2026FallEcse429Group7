"""API under test: HEAD /projects/:id/tasks (documented) - headers of the project's todo list."""
import pytest

from task_link_support import JSON, XML, project_tasks_path, send_raw

pytestmark = pytest.mark.documented


def test_returns_200_with_empty_body(api, create_project):
    project_id = create_project()

    response = send_raw(api, "HEAD", project_tasks_path(project_id))

    assert response.status_code == 200
    assert response.text == ""


def test_declares_json_content_type_by_default(api, create_project):
    project_id = create_project()

    response = send_raw(api, "HEAD", project_tasks_path(project_id))

    assert response.headers["Content-Type"].startswith(JSON)


def test_declares_xml_content_type_when_xml_is_accepted(api, create_project):
    project_id = create_project()

    response = send_raw(api, "HEAD", project_tasks_path(project_id), accept=XML)

    assert response.headers["Content-Type"].startswith(XML)


def test_does_not_change_the_link_list(api, create_project, create_todo, link_todo_to_project):
    project_id, todo_id = create_project(), create_todo()
    link_todo_to_project(project_id, todo_id)

    send_raw(api, "HEAD", project_tasks_path(project_id))

    todos = api.get(project_tasks_path(project_id)).json()["todos"]
    assert [todo["id"] for todo in todos] == [todo_id]
