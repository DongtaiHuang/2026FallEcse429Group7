"""Invalid operations: HTTP methods swagger marks 405 on the task-link paths and the app rejects as such.

GET, POST and HEAD on the link item paths are in the bug 5 modules because the app answers 404 there.
"""
import pytest

from task_link_support import ids_in, project_tasks_path, send_raw, todo_projects_path


@pytest.mark.parametrize("method", ["PUT", "PATCH", "DELETE"])
def test_project_tasks_collection_rejects_method_with_405(api, create_project, create_todo, link_todo_to_project, method):
    project_id, todo_id = create_project(), create_todo()
    link_todo_to_project(project_id, todo_id)

    response = send_raw(api, method, project_tasks_path(project_id), body=f'{{"id": "{todo_id}"}}')

    assert response.status_code == 405
    assert ids_in(api.get(project_tasks_path(project_id)), "todos") == [todo_id]


@pytest.mark.parametrize("method", ["PUT", "PATCH", "DELETE"])
def test_todo_tasksof_collection_rejects_method_with_405(api, create_project, create_todo, link_todo_to_project, method):
    project_id, todo_id = create_project(), create_todo()
    link_todo_to_project(project_id, todo_id)

    response = send_raw(api, method, todo_projects_path(todo_id), body=f'{{"id": "{project_id}"}}')

    assert response.status_code == 405
    assert ids_in(api.get(todo_projects_path(todo_id)), "projects") == [project_id]


@pytest.mark.parametrize("method", ["PUT", "PATCH"])
def test_project_task_link_item_rejects_method_with_405(api, create_project, create_todo, link_todo_to_project, method):
    project_id, todo_id = create_project(), create_todo()
    link_todo_to_project(project_id, todo_id)

    response = send_raw(api, method, f"{project_tasks_path(project_id)}/{todo_id}", body="{}")

    assert response.status_code == 405
    assert ids_in(api.get(project_tasks_path(project_id)), "todos") == [todo_id]


@pytest.mark.parametrize("method", ["PUT", "PATCH"])
def test_todo_tasksof_link_item_rejects_method_with_405(api, create_project, create_todo, link_todo_to_project, method):
    project_id, todo_id = create_project(), create_todo()
    link_todo_to_project(project_id, todo_id)

    response = send_raw(api, method, f"{todo_projects_path(todo_id)}/{project_id}", body="{}")

    assert response.status_code == 405
    assert ids_in(api.get(todo_projects_path(todo_id)), "projects") == [project_id]
