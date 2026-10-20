"""BUG 1 - EXPECTED behaviour (FAILS today): GET/HEAD of task links for a parent that does not exist.

A missing project or todo should give 404 and no data, like GET /projects/:id and GET /todos/:id.
The matching passing module is test_bug01_missing_parent_get_actual.py.
"""
import pytest

from task_link_support import MISSING_ID, project_tasks_path, send_raw, todo_projects_path

pytestmark = pytest.mark.bug_expected

MISSING_PARENT_PATHS = {
    "project": (project_tasks_path(MISSING_ID), "todos"),
    "todo": (todo_projects_path(MISSING_ID), "projects"),
}


@pytest.fixture
def existing_link(create_project, create_todo, link_todo_to_project):
    """Data that the buggy endpoints leak into the response for a missing parent."""
    project_id, todo_id = create_project(), create_todo()
    link_todo_to_project(project_id, todo_id)
    return project_id, todo_id


@pytest.mark.parametrize("path,_", MISSING_PARENT_PATHS.values(), ids=MISSING_PARENT_PATHS.keys())
def test_get_for_missing_parent_returns_404(api, existing_link, path, _):
    response = api.get(path)

    assert response.status_code == 404


@pytest.mark.parametrize("path,key", MISSING_PARENT_PATHS.values(), ids=MISSING_PARENT_PATHS.keys())
def test_get_for_missing_parent_returns_no_related_items(api, existing_link, path, key):
    response = api.get(path)

    assert response.json().get(key, []) == []


@pytest.mark.parametrize("path,_", MISSING_PARENT_PATHS.values(), ids=MISSING_PARENT_PATHS.keys())
def test_head_for_missing_parent_returns_404(api, existing_link, path, _):
    response = send_raw(api, "HEAD", path)

    assert response.status_code == 404
