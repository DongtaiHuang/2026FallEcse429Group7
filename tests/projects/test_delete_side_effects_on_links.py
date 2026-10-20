"""API under test: DELETE /projects/:id and DELETE /todos/:id seen from the task links (undocumented effects).

Deleting an entity removes its links but never deletes the entity on the other side (no cascade).
"""
import pytest

from task_link_support import ids_in, project_tasks_path, todo_projects_path

pytestmark = pytest.mark.undocumented


def test_deleting_a_project_keeps_its_todos(api, create_project, create_todo, link_todo_to_project):
    project_id, first_todo, second_todo = create_project(), create_todo(), create_todo()
    link_todo_to_project(project_id, first_todo)
    link_todo_to_project(project_id, second_todo)

    assert api.delete(f"/projects/{project_id}").status_code == 200

    assert api.get(f"/todos/{first_todo}").status_code == 200
    assert api.get(f"/todos/{second_todo}").status_code == 200


def test_deleting_a_project_removes_it_from_its_todos(api, create_project, create_todo, link_todo_to_project):
    project_id, todo_id = create_project(), create_todo()
    link_todo_to_project(project_id, todo_id)

    api.delete(f"/projects/{project_id}")

    assert ids_in(api.get(todo_projects_path(todo_id)), "projects") == []
    assert "tasksof" not in api.get(f"/todos/{todo_id}").json()["todos"][0]


def test_deleting_a_todo_keeps_its_projects(api, create_project, create_todo, link_todo_to_project):
    first_project, second_project, todo_id = create_project(), create_project(), create_todo()
    link_todo_to_project(first_project, todo_id)
    link_todo_to_project(second_project, todo_id)

    assert api.delete(f"/todos/{todo_id}").status_code == 200

    assert api.get(f"/projects/{first_project}").status_code == 200
    assert api.get(f"/projects/{second_project}").status_code == 200


def test_deleting_a_todo_removes_it_from_its_projects(api, create_project, create_todo, link_todo_to_project):
    project_id, todo_id = create_project(), create_todo()
    link_todo_to_project(project_id, todo_id)

    api.delete(f"/todos/{todo_id}")

    assert ids_in(api.get(project_tasks_path(project_id)), "todos") == []
    assert "tasks" not in api.get(f"/projects/{project_id}").json()["projects"][0]


def test_deleting_one_todo_leaves_the_projects_other_todos(api, create_project, create_todo, link_todo_to_project):
    project_id, deleted_todo, kept_todo = create_project(), create_todo(), create_todo()
    link_todo_to_project(project_id, deleted_todo)
    link_todo_to_project(project_id, kept_todo)

    api.delete(f"/todos/{deleted_todo}")

    assert ids_in(api.get(project_tasks_path(project_id)), "todos") == [kept_todo]


def test_deleted_project_cannot_be_deleted_again(api, create_project):
    project_id = create_project()
    api.delete(f"/projects/{project_id}")

    response = api.delete(f"/projects/{project_id}")

    assert response.status_code == 404
