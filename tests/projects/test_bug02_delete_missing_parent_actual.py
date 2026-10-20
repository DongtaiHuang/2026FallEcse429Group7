"""BUG 2 - ACTUAL behaviour (PASSES today): DELETE of a link whose parent does not exist.

When the child is linked to another parent, the app answers 400 and leaks a Java NullPointerException
message; when the child has no links it answers a clean 404. Expected behaviour is in
test_bug02_delete_missing_parent_expected.py.
"""
import pytest

from task_link_support import MISSING_ID, ids_in, project_tasks_path, todo_projects_path

pytestmark = pytest.mark.bug_actual

NPE_TEXT = "Cannot invoke"


@pytest.fixture
def linked_pair(create_project, create_todo, link_todo_to_project):
    project_id, todo_id = create_project(), create_todo()
    link_todo_to_project(project_id, todo_id)
    return project_id, todo_id


def test_delete_with_missing_project_and_linked_todo_returns_400_with_java_message(api, linked_pair):
    _, todo_id = linked_pair

    response = api.delete(f"{project_tasks_path(MISSING_ID)}/{todo_id}")

    assert response.status_code == 400
    assert NPE_TEXT in response.text
    assert response.headers["Content-Type"].startswith("text/html")


def test_delete_with_missing_todo_and_linked_project_returns_400_with_java_message(api, linked_pair):
    project_id, _ = linked_pair

    response = api.delete(f"{todo_projects_path(MISSING_ID)}/{project_id}")

    assert response.status_code == 400
    assert NPE_TEXT in response.text


def test_failed_delete_leaves_the_existing_link_untouched(api, linked_pair):
    project_id, todo_id = linked_pair

    api.delete(f"{project_tasks_path(MISSING_ID)}/{todo_id}")
    api.delete(f"{todo_projects_path(MISSING_ID)}/{project_id}")

    assert ids_in(api.get(project_tasks_path(project_id)), "todos") == [todo_id]


def test_delete_with_missing_project_and_unlinked_todo_returns_clean_404(api, create_todo):
    unlinked_todo = create_todo()

    response = api.delete(f"{project_tasks_path(MISSING_ID)}/{unlinked_todo}")

    assert response.status_code == 404
    assert NPE_TEXT not in response.text


def test_delete_with_missing_todo_and_unlinked_project_returns_clean_404(api, create_project):
    unlinked_project = create_project()

    response = api.delete(f"{todo_projects_path(MISSING_ID)}/{unlinked_project}")

    assert response.status_code == 404
    assert NPE_TEXT not in response.text
