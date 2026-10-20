"""API under test: GET /todos/:id/tasksof (documented) - list the projects a todo belongs to."""
import pytest

from task_link_support import JSON, XML, ids_in, send_raw, todo_projects_path, xml_root

pytestmark = pytest.mark.documented


def test_returns_200_with_json_content_type(api, create_todo):
    todo_id = create_todo()

    response = api.get(todo_projects_path(todo_id))

    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith(JSON)


def test_todo_without_projects_returns_empty_list(api, create_todo):
    todo_id = create_todo()

    response = api.get(todo_projects_path(todo_id))

    assert response.json() == {"projects": []}


def test_lists_linked_project_with_its_fields(api, create_project, create_todo, link_todo_to_project):
    project_id = create_project(title="Website redesign", description="Q4 relaunch")
    todo_id = create_todo()
    link_todo_to_project(project_id, todo_id)

    projects = api.get(todo_projects_path(todo_id)).json()["projects"]

    assert projects == [{
        "id": project_id,
        "title": "Website redesign",
        "completed": "false",
        "active": "false",
        "description": "Q4 relaunch",
        "tasks": [{"id": todo_id}],
    }]


def test_lists_every_project_of_the_todo(api, create_project, create_todo, link_todo_to_project):
    todo_id = create_todo()
    project_ids = [create_project(), create_project()]
    for project_id in project_ids:
        link_todo_to_project(project_id, todo_id)

    response = api.get(todo_projects_path(todo_id))

    assert sorted(ids_in(response, "projects")) == sorted(project_ids)


def test_does_not_list_projects_linked_to_other_todos(api, create_project, create_todo, link_todo_to_project):
    todo_id, other_todo_id = create_todo(), create_todo()
    own_project, other_project = create_project(), create_project()
    link_todo_to_project(own_project, todo_id)
    link_todo_to_project(other_project, other_todo_id)

    response = api.get(todo_projects_path(todo_id))

    assert ids_in(response, "projects") == [own_project]


@pytest.mark.default_data
def test_default_todos_belong_to_the_default_project(api):
    """Needs the application's startup data (todos 1 and 2 in project 1)."""
    assert "1" in ids_in(api.get(todo_projects_path(1)), "projects")
    assert "1" in ids_in(api.get(todo_projects_path(2)), "projects")


def test_returns_xml_when_requested(api, create_project, create_todo, link_todo_to_project):
    project_id, todo_id = create_project(), create_todo()
    link_todo_to_project(project_id, todo_id)

    response = send_raw(api, "GET", todo_projects_path(todo_id), accept=XML)

    root = xml_root(response)
    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith(XML)
    assert root.tag == "projects"
    assert root.findtext("project/id") == project_id
    assert root.findtext("project/tasks/id") == todo_id
