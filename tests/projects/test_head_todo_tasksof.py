"""API under test: HEAD /todos/:id/tasksof (documented) - headers of the todo's project list."""
import pytest

from task_link_support import JSON, XML, send_raw, todo_projects_path

pytestmark = pytest.mark.documented


def test_returns_200_with_empty_body(api, create_todo):
    todo_id = create_todo()

    response = send_raw(api, "HEAD", todo_projects_path(todo_id))

    assert response.status_code == 200
    assert response.text == ""


def test_declares_json_content_type_by_default(api, create_todo):
    todo_id = create_todo()

    response = send_raw(api, "HEAD", todo_projects_path(todo_id))

    assert response.headers["Content-Type"].startswith(JSON)


def test_declares_xml_content_type_when_xml_is_accepted(api, create_todo):
    todo_id = create_todo()

    response = send_raw(api, "HEAD", todo_projects_path(todo_id), accept=XML)

    assert response.headers["Content-Type"].startswith(XML)


def test_does_not_change_the_link_list(api, create_project, create_todo, link_todo_to_project):
    project_id, todo_id = create_project(), create_todo()
    link_todo_to_project(project_id, todo_id)

    send_raw(api, "HEAD", todo_projects_path(todo_id))

    projects = api.get(todo_projects_path(todo_id)).json()["projects"]
    assert [project["id"] for project in projects] == [project_id]
