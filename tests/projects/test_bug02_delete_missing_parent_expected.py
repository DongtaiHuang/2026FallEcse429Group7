"""BUG 2 - EXPECTED behaviour (FAILS today): DELETE of a link whose parent does not exist.

Should be 404 with a clean message, whether or not the child is linked elsewhere.
The matching passing module is test_bug02_delete_missing_parent_actual.py.
"""
import pytest

from task_link_support import MISSING_ID, project_tasks_path, todo_projects_path

pytestmark = pytest.mark.bug_expected


@pytest.fixture
def linked_pair(create_project, create_todo, link_todo_to_project):
    project_id, todo_id = create_project(), create_todo()
    link_todo_to_project(project_id, todo_id)
    return project_id, todo_id


def test_delete_with_missing_project_returns_404_when_todo_is_linked(api, linked_pair):
    _, todo_id = linked_pair

    response = api.delete(f"{project_tasks_path(MISSING_ID)}/{todo_id}")

    assert response.status_code == 404


def test_delete_with_missing_todo_returns_404_when_project_is_linked(api, linked_pair):
    project_id, _ = linked_pair

    response = api.delete(f"{todo_projects_path(MISSING_ID)}/{project_id}")

    assert response.status_code == 404


def test_delete_with_missing_project_does_not_expose_java_internals(api, linked_pair):
    _, todo_id = linked_pair

    response = api.delete(f"{project_tasks_path(MISSING_ID)}/{todo_id}")

    assert "Cannot invoke" not in response.text


def test_delete_with_missing_todo_does_not_expose_java_internals(api, linked_pair):
    project_id, _ = linked_pair

    response = api.delete(f"{todo_projects_path(MISSING_ID)}/{project_id}")

    assert "Cannot invoke" not in response.text
