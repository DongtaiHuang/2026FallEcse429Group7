"""BUG 4 - EXPECTED behaviour (FAILS today): GET, POST and HEAD on the link item paths.

Swagger lists 405 Method Not Allowed for these methods on /projects/:id/tasks/:id and
/todos/:id/tasksof/:id. The matching passing module is test_bug04_item_path_methods_actual.py.
"""
import pytest

from task_link_support import project_tasks_path, send_raw, todo_projects_path

pytestmark = pytest.mark.bug_expected

METHODS = ["GET", "POST", "HEAD"]


@pytest.mark.parametrize("method", METHODS)
def test_project_task_link_item_returns_405(api, create_project, create_todo, link_todo_to_project, method):
    project_id, todo_id = create_project(), create_todo()
    link_todo_to_project(project_id, todo_id)

    response = send_raw(api, method, f"{project_tasks_path(project_id)}/{todo_id}", body="{}" if method == "POST" else None)

    assert response.status_code == 405


@pytest.mark.parametrize("method", METHODS)
def test_todo_tasksof_link_item_returns_405(api, create_project, create_todo, link_todo_to_project, method):
    project_id, todo_id = create_project(), create_todo()
    link_todo_to_project(project_id, todo_id)

    response = send_raw(api, method, f"{todo_projects_path(todo_id)}/{project_id}", body="{}" if method == "POST" else None)

    assert response.status_code == 405
