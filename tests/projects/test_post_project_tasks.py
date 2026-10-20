"""API under test: POST /projects/:id/tasks (documented) - link an existing todo to a project."""
import pytest

from task_link_support import MISSING_ID, ids_in, project_tasks_path, todo_projects_path

pytestmark = pytest.mark.documented


def test_link_returns_201_with_empty_body(api, create_project, create_todo, state):
    project_id, todo_id = create_project(), create_todo()

    response = api.post(project_tasks_path(project_id), data={"id": todo_id})
    state.track_relationship("projects", project_id, "tasks", todo_id)

    assert response.status_code == 201
    assert response.text == ""


def test_linked_todo_is_listed_by_the_project(api, create_project, create_todo, link_todo_to_project):
    project_id, todo_id = create_project(), create_todo()

    link_todo_to_project(project_id, todo_id)

    assert ids_in(api.get(project_tasks_path(project_id)), "todos") == [todo_id]


def test_link_is_visible_from_the_todo_side(api, create_project, create_todo, link_todo_to_project):
    project_id, todo_id = create_project(), create_todo()

    link_todo_to_project(project_id, todo_id)

    assert ids_in(api.get(todo_projects_path(todo_id)), "projects") == [project_id]


def test_project_and_todo_bodies_embed_the_link(api, create_project, create_todo, link_todo_to_project):
    project_id, todo_id = create_project(), create_todo()

    link_todo_to_project(project_id, todo_id)

    project = api.get(f"/projects/{project_id}").json()["projects"][0]
    todo = api.get(f"/todos/{todo_id}").json()["todos"][0]
    assert project["tasks"] == [{"id": todo_id}]
    assert todo["tasksof"] == [{"id": project_id}]


def test_link_leaves_project_and_todo_fields_unchanged(api, create_project, create_todo, link_todo_to_project):
    project_id = create_project(title="Website redesign", description="Q4 relaunch")
    todo_id = create_todo(title="Write homepage copy", description="First draft")

    link_todo_to_project(project_id, todo_id)

    project = api.get(f"/projects/{project_id}").json()["projects"][0]
    todo = api.get(f"/todos/{todo_id}").json()["todos"][0]
    assert (project["title"], project["description"]) == ("Website redesign", "Q4 relaunch")
    assert (todo["title"], todo["description"], todo["doneStatus"]) == ("Write homepage copy", "First draft", "false")


def test_link_does_not_touch_unrelated_todos(api, create_project, create_todo, link_todo_to_project):
    project_id, todo_id, unrelated_id = create_project(), create_todo(), create_todo()

    link_todo_to_project(project_id, todo_id)

    unrelated = api.get(f"/todos/{unrelated_id}").json()["todos"][0]
    assert "tasksof" not in unrelated


def test_one_todo_can_belong_to_several_projects(api, create_project, create_todo, link_todo_to_project):
    first_project, second_project, todo_id = create_project(), create_project(), create_todo()

    link_todo_to_project(first_project, todo_id)
    link_todo_to_project(second_project, todo_id)

    projects = ids_in(api.get(todo_projects_path(todo_id)), "projects")
    assert sorted(projects) == sorted([first_project, second_project])


@pytest.mark.parametrize("missing_todo_id", [MISSING_ID, "abc"])
def test_unknown_todo_id_returns_404_and_creates_no_link(api, create_project, missing_todo_id):
    project_id = create_project()

    response = api.post(project_tasks_path(project_id), data={"id": missing_todo_id})

    assert response.status_code == 404
    assert "errorMessages" in response.json()
    assert api.get(project_tasks_path(project_id)).json() == {"todos": []}


def test_unknown_project_returns_404_and_creates_no_link(api, create_todo):
    todo_id = create_todo()

    response = api.post(project_tasks_path(MISSING_ID), data={"id": todo_id})

    assert response.status_code == 404
    assert "errorMessages" in response.json()
    assert api.get(todo_projects_path(todo_id)).json() == {"projects": []}


def test_numeric_json_id_is_currently_rejected_with_404(api, create_project, create_todo):
    """Current behaviour (not documented): only the string form of an id can be used to link."""
    project_id, todo_id = create_project(), create_todo()

    response = api.post(project_tasks_path(project_id), data={"id": int(todo_id)})

    assert response.status_code == 404
    assert api.get(project_tasks_path(project_id)).json() == {"todos": []}
