"""BUG 1 - ACTUAL behaviour (PASSES today): GET/HEAD of task links for a parent that does not exist.

The app answers 200 and lists items that belong to OTHER parents. The expected behaviour is in
test_bug01_missing_parent_get_expected.py.
"""
import pytest

from task_link_support import MISSING_ID, ids_in, project_tasks_path, send_raw, todo_projects_path

pytestmark = pytest.mark.bug_actual


@pytest.fixture
def existing_link(create_project, create_todo, link_todo_to_project):
    project_id, todo_id = create_project(), create_todo()
    link_todo_to_project(project_id, todo_id)
    return project_id, todo_id


def test_control_missing_parents_really_do_not_exist(api):
    assert api.get(f"/projects/{MISSING_ID}").status_code == 404
    assert api.get(f"/todos/{MISSING_ID}").status_code == 404


def test_get_tasks_of_missing_project_returns_200_with_todos_of_other_projects(api, existing_link):
    _, todo_id = existing_link

    response = api.get(project_tasks_path(MISSING_ID))

    assert response.status_code == 200
    assert todo_id in ids_in(response, "todos")


def test_get_tasksof_of_missing_todo_returns_200_with_projects_of_other_todos(api, existing_link):
    project_id, _ = existing_link

    response = api.get(todo_projects_path(MISSING_ID))

    assert response.status_code == 200
    assert project_id in ids_in(response, "projects")


def test_get_for_missing_parent_leaves_only_linked_todos_in_the_list(api, existing_link, create_todo):
    unlinked_todo = create_todo()

    response = api.get(project_tasks_path(MISSING_ID))

    assert unlinked_todo not in ids_in(response, "todos")


@pytest.mark.parametrize("path", [project_tasks_path(MISSING_ID), todo_projects_path(MISSING_ID)], ids=["project", "todo"])
def test_head_for_missing_parent_returns_200(api, path):
    response = send_raw(api, "HEAD", path)

    assert response.status_code == 200
    assert response.text == ""
