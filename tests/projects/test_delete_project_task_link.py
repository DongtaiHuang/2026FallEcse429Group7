"""API under test: DELETE /projects/:id/tasks/:id (documented) - remove the link between a project and a todo."""
import pytest

from task_link_support import MISSING_ID, ids_in, project_tasks_path, todo_projects_path

pytestmark = pytest.mark.documented


def link_path(project_id, todo_id):
    return f"{project_tasks_path(project_id)}/{todo_id}"


def test_unlink_returns_200_with_empty_body(api, create_project, create_todo, link_todo_to_project):
    project_id, todo_id = create_project(), create_todo()
    link_todo_to_project(project_id, todo_id)

    response = api.delete(link_path(project_id, todo_id))

    assert response.status_code == 200
    assert response.text == ""


def test_unlink_removes_the_link_from_both_sides(api, create_project, create_todo, link_todo_to_project):
    project_id, todo_id = create_project(), create_todo()
    link_todo_to_project(project_id, todo_id)

    api.delete(link_path(project_id, todo_id))

    assert ids_in(api.get(project_tasks_path(project_id)), "todos") == []
    assert ids_in(api.get(todo_projects_path(todo_id)), "projects") == []


def test_unlink_keeps_both_the_project_and_the_todo(api, create_project, create_todo, link_todo_to_project):
    project_id, todo_id = create_project(), create_todo()
    link_todo_to_project(project_id, todo_id)

    api.delete(link_path(project_id, todo_id))

    assert api.get(f"/projects/{project_id}").status_code == 200
    assert api.get(f"/todos/{todo_id}").status_code == 200


def test_unlink_keeps_the_other_links(api, create_project, create_todo, link_todo_to_project):
    project_id, other_project_id = create_project(), create_project()
    todo_id, other_todo_id = create_todo(), create_todo()
    link_todo_to_project(project_id, todo_id)
    link_todo_to_project(project_id, other_todo_id)
    link_todo_to_project(other_project_id, todo_id)

    api.delete(link_path(project_id, todo_id))

    assert ids_in(api.get(project_tasks_path(project_id)), "todos") == [other_todo_id]
    assert ids_in(api.get(todo_projects_path(todo_id)), "projects") == [other_project_id]


def test_deleting_the_same_link_twice_returns_404(api, create_project, create_todo, link_todo_to_project):
    project_id, todo_id = create_project(), create_todo()
    link_todo_to_project(project_id, todo_id)
    api.delete(link_path(project_id, todo_id))

    response = api.delete(link_path(project_id, todo_id))

    assert response.status_code == 404
    assert "errorMessages" in response.json()


def test_deleting_a_link_that_never_existed_returns_404(api, create_project, create_todo):
    project_id, todo_id = create_project(), create_todo()

    response = api.delete(link_path(project_id, todo_id))

    assert response.status_code == 404


@pytest.mark.parametrize("bad_todo_id", [MISSING_ID, "abc"])
def test_unknown_todo_id_returns_404_and_keeps_existing_links(api, create_project, create_todo, link_todo_to_project, bad_todo_id):
    project_id, todo_id = create_project(), create_todo()
    link_todo_to_project(project_id, todo_id)

    response = api.delete(link_path(project_id, bad_todo_id))

    assert response.status_code == 404
    assert ids_in(api.get(project_tasks_path(project_id)), "todos") == [todo_id]
