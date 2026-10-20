"""BUG 4 - ACTUAL behaviour (PASSES today): GET, POST and HEAD on the link item paths answer 404.

The body is empty and the Content-Type is text/html. The link itself is not affected. Expected
behaviour (405, per swagger) is in test_bug04_item_path_methods_expected.py.
"""
import pytest

from task_link_support import ids_in, project_tasks_path, send_raw, todo_projects_path

pytestmark = pytest.mark.bug_actual

METHODS = ["GET", "POST", "HEAD"]


@pytest.mark.parametrize("method", METHODS)
def test_project_task_link_item_returns_404(api, create_project, create_todo, link_todo_to_project, method):
    project_id, todo_id = create_project(), create_todo()
    link_todo_to_project(project_id, todo_id)

    response = send_raw(api, method, f"{project_tasks_path(project_id)}/{todo_id}", body="{}" if method == "POST" else None)

    assert response.status_code == 404
    assert response.text == ""
    assert ids_in(api.get(project_tasks_path(project_id)), "todos") == [todo_id]


@pytest.mark.parametrize("method", METHODS)
def test_todo_tasksof_link_item_returns_404(api, create_project, create_todo, link_todo_to_project, method):
    project_id, todo_id = create_project(), create_todo()
    link_todo_to_project(project_id, todo_id)

    response = send_raw(api, method, f"{todo_projects_path(todo_id)}/{project_id}", body="{}" if method == "POST" else None)

    assert response.status_code == 404
    assert response.text == ""
    assert ids_in(api.get(todo_projects_path(todo_id)), "projects") == [project_id]
