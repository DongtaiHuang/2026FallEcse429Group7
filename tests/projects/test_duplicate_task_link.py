"""API under test: POST /projects/:id/tasks and POST /todos/:id/tasksof sent twice for the same pair (undocumented)."""
import pytest

from task_link_support import ids_in, project_tasks_path, todo_projects_path

pytestmark = pytest.mark.undocumented


def test_duplicate_project_side_link_is_accepted_with_201(api, create_project, create_todo, link_todo_to_project):
    project_id, todo_id = create_project(), create_todo()
    link_todo_to_project(project_id, todo_id)

    response = api.post(project_tasks_path(project_id), data={"id": todo_id})

    assert response.status_code == 201


def test_duplicate_todo_side_link_is_accepted_with_201(api, create_project, create_todo, link_todo_to_project):
    project_id, todo_id = create_project(), create_todo()
    link_todo_to_project(project_id, todo_id)

    response = api.post(todo_projects_path(todo_id), data={"id": project_id})

    assert response.status_code == 201


def test_duplicate_link_is_stored_only_once(api, create_project, create_todo, link_todo_to_project):
    project_id, todo_id = create_project(), create_todo()
    link_todo_to_project(project_id, todo_id)
    api.post(project_tasks_path(project_id), data={"id": todo_id})

    assert ids_in(api.get(project_tasks_path(project_id)), "todos") == [todo_id]
    assert ids_in(api.get(todo_projects_path(todo_id)), "projects") == [project_id]


def test_one_delete_removes_a_link_that_was_posted_twice(api, create_project, create_todo, link_todo_to_project):
    project_id, todo_id = create_project(), create_todo()
    link_todo_to_project(project_id, todo_id)
    api.post(project_tasks_path(project_id), data={"id": todo_id})

    api.delete(f"{project_tasks_path(project_id)}/{todo_id}")

    assert ids_in(api.get(project_tasks_path(project_id)), "todos") == []
