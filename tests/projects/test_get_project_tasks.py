"""API under test: GET /projects/:id/tasks (documented) - list the todos linked to a project."""
import pytest

from task_link_support import JSON, XML, ids_in, project_tasks_path, send_raw, xml_root

pytestmark = pytest.mark.documented


def test_returns_200_with_json_content_type(api, create_project):
    project_id = create_project()

    response = api.get(project_tasks_path(project_id))

    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith(JSON)


def test_project_without_todos_returns_empty_list(api, create_project):
    project_id = create_project()

    response = api.get(project_tasks_path(project_id))

    assert response.json() == {"todos": []}


def test_lists_linked_todo_with_its_fields(api, create_project, create_todo, link_todo_to_project):
    project_id = create_project()
    todo_id = create_todo(title="Write homepage copy", description="First draft")
    link_todo_to_project(project_id, todo_id)

    todos = api.get(project_tasks_path(project_id)).json()["todos"]

    assert todos == [{
        "id": todo_id,
        "title": "Write homepage copy",
        "doneStatus": "false",
        "description": "First draft",
        "tasksof": [{"id": project_id}],
    }]


def test_lists_every_linked_todo(api, create_project, create_todo, link_todo_to_project):
    project_id = create_project()
    todo_ids = [create_todo(), create_todo(), create_todo()]
    for todo_id in todo_ids:
        link_todo_to_project(project_id, todo_id)

    response = api.get(project_tasks_path(project_id))

    assert sorted(ids_in(response, "todos")) == sorted(todo_ids)


def test_does_not_list_todos_linked_to_other_projects(api, create_project, create_todo, link_todo_to_project):
    project_id, other_project_id = create_project(), create_project()
    own_todo, other_todo, unlinked_todo = create_todo(), create_todo(), create_todo()
    link_todo_to_project(project_id, own_todo)
    link_todo_to_project(other_project_id, other_todo)

    response = api.get(project_tasks_path(project_id))

    assert ids_in(response, "todos") == [own_todo]
    assert unlinked_todo not in ids_in(response, "todos")


@pytest.mark.default_data
def test_default_project_lists_the_default_todos(api):
    """Needs the application's startup data (project 1 with todos 1 and 2)."""
    response = api.get(project_tasks_path(1))

    assert {"1", "2"} <= set(ids_in(response, "todos"))


def test_returns_xml_when_requested(api, create_project, create_todo, link_todo_to_project):
    project_id, todo_id = create_project(), create_todo()
    link_todo_to_project(project_id, todo_id)

    response = send_raw(api, "GET", project_tasks_path(project_id), accept=XML)

    root = xml_root(response)
    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith(XML)
    assert root.tag == "todos"
    assert root.findtext("todo/id") == todo_id
    assert root.findtext("todo/tasksof/id") == project_id


def test_unsupported_accept_type_returns_406(api, create_project):
    project_id = create_project()

    response = send_raw(api, "GET", project_tasks_path(project_id), accept="text/plain")

    assert response.status_code == 406
