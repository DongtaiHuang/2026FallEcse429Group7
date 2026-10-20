"""API under test: POST /todos and POST /projects with an inline link field (undocumented).

A `tasksof` list on a new todo, or a `tasks` list on a new project, creates the link at creation time.
"""
import pytest

from task_link_support import ids_in, project_tasks_path, todo_projects_path

pytestmark = pytest.mark.undocumented


def test_todo_created_with_tasksof_is_linked_to_the_project(api, create_project, state):
    project_id = create_project()

    response = api.post("/todos", data={"title": "Write homepage copy", "tasksof": [{"id": project_id}]})
    todo_id = response.json()["id"]
    state.track_created("todos", todo_id)

    assert response.status_code == 201
    assert response.json()["tasksof"] == [{"id": project_id}]


def test_inline_tasksof_is_visible_from_the_project_side(api, create_project, state):
    project_id = create_project()
    todo_id = api.post("/todos", data={"title": "Write homepage copy", "tasksof": [{"id": project_id}]}).json()["id"]
    state.track_created("todos", todo_id)

    assert ids_in(api.get(project_tasks_path(project_id)), "todos") == [todo_id]


def test_project_created_with_tasks_is_linked_to_the_todo(api, create_todo, state):
    todo_id = create_todo()

    response = api.post("/projects", data={"title": "Marketing campaign", "tasks": [{"id": todo_id}]})
    project_id = response.json()["id"]
    state.track_created("projects", project_id)

    assert response.status_code == 201
    assert response.json()["tasks"] == [{"id": todo_id}]


def test_inline_tasks_is_visible_from_the_todo_side(api, create_todo, state):
    todo_id = create_todo()
    project_id = api.post("/projects", data={"title": "Marketing campaign", "tasks": [{"id": todo_id}]}).json()["id"]
    state.track_created("projects", project_id)

    assert ids_in(api.get(todo_projects_path(todo_id)), "projects") == [project_id]


def test_inline_link_adds_to_the_links_the_todo_already_has(api, create_project, create_todo, link_todo_to_project, state):
    first_project, second_project, todo_id = create_project(), create_project(), create_todo()
    link_todo_to_project(first_project, todo_id)
    new_project = api.post("/projects", data={"title": "Second", "tasks": [{"id": todo_id}]}).json()["id"]
    state.track_created("projects", new_project)

    projects = ids_in(api.get(todo_projects_path(todo_id)), "projects")

    assert sorted(projects) == sorted([first_project, new_project])
    assert second_project not in projects
