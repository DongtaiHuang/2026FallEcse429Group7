"""API under test: OPTIONS on the four task-link paths (swagger only, absent from the /docs page)."""
import pytest

from task_link_support import allowed_methods, project_tasks_path, send_raw, todo_projects_path

pytestmark = pytest.mark.undocumented

COLLECTION_METHODS = {"OPTIONS", "GET", "HEAD", "POST"}
ITEM_METHODS = {"OPTIONS", "DELETE"}


def test_project_tasks_collection_advertises_its_methods(api, create_project):
    project_id = create_project()

    response = send_raw(api, "OPTIONS", project_tasks_path(project_id))

    assert response.status_code == 200
    assert allowed_methods(response) == COLLECTION_METHODS


def test_todo_tasksof_collection_advertises_its_methods(api, create_todo):
    todo_id = create_todo()

    response = send_raw(api, "OPTIONS", todo_projects_path(todo_id))

    assert response.status_code == 200
    assert allowed_methods(response) == COLLECTION_METHODS


def test_project_task_link_item_advertises_delete_only(api, create_project, create_todo):
    project_id, todo_id = create_project(), create_todo()

    response = send_raw(api, "OPTIONS", f"{project_tasks_path(project_id)}/{todo_id}")

    assert response.status_code == 200
    assert allowed_methods(response) == ITEM_METHODS


def test_todo_tasksof_link_item_advertises_delete_only(api, create_project, create_todo):
    project_id, todo_id = create_project(), create_todo()

    response = send_raw(api, "OPTIONS", f"{todo_projects_path(todo_id)}/{project_id}")

    assert response.status_code == 200
    assert allowed_methods(response) == ITEM_METHODS


def test_options_returns_an_empty_body(api, create_project):
    project_id = create_project()

    response = send_raw(api, "OPTIONS", project_tasks_path(project_id))

    assert response.text == ""
