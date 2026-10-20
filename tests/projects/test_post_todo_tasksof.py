"""API under test: POST /todos/:id/tasksof (documented) - link an existing project to a todo."""
import pytest

from task_link_support import MISSING_ID, ids_in, project_tasks_path, todo_projects_path

pytestmark = pytest.mark.documented


@pytest.fixture
def link_project_to_todo(api, state):
    """Arrange step through the todo-side call, with the undo registered."""

    def link(todo_id, project_id):
        response = api.post(todo_projects_path(todo_id), data={"id": project_id})
        assert response.status_code == 201, response.text
        state.track_relationship("todos", todo_id, "tasksof", project_id)

    return link


def test_link_returns_201_with_empty_body(api, create_project, create_todo, state):
    project_id, todo_id = create_project(), create_todo()

    response = api.post(todo_projects_path(todo_id), data={"id": project_id})
    state.track_relationship("todos", todo_id, "tasksof", project_id)

    assert response.status_code == 201
    assert response.text == ""


def test_linked_project_is_listed_by_the_todo(api, create_project, create_todo, link_project_to_todo):
    project_id, todo_id = create_project(), create_todo()

    link_project_to_todo(todo_id, project_id)

    assert ids_in(api.get(todo_projects_path(todo_id)), "projects") == [project_id]


def test_link_is_visible_from_the_project_side(api, create_project, create_todo, link_project_to_todo):
    project_id, todo_id = create_project(), create_todo()

    link_project_to_todo(todo_id, project_id)

    assert ids_in(api.get(project_tasks_path(project_id)), "todos") == [todo_id]


def test_project_and_todo_bodies_embed_the_link(api, create_project, create_todo, link_project_to_todo):
    project_id, todo_id = create_project(), create_todo()

    link_project_to_todo(todo_id, project_id)

    project = api.get(f"/projects/{project_id}").json()["projects"][0]
    todo = api.get(f"/todos/{todo_id}").json()["todos"][0]
    assert project["tasks"] == [{"id": todo_id}]
    assert todo["tasksof"] == [{"id": project_id}]


def test_link_leaves_todo_fields_unchanged(api, create_project, create_todo, link_project_to_todo):
    project_id = create_project()
    todo_id = create_todo(title="Draft launch email", description="Send on Monday", doneStatus=True)

    link_project_to_todo(todo_id, project_id)

    todo = api.get(f"/todos/{todo_id}").json()["todos"][0]
    assert (todo["title"], todo["description"], todo["doneStatus"]) == ("Draft launch email", "Send on Monday", "true")


def test_link_does_not_touch_unrelated_projects(api, create_project, create_todo, link_project_to_todo):
    project_id, unrelated_id, todo_id = create_project(), create_project(), create_todo()

    link_project_to_todo(todo_id, project_id)

    unrelated = api.get(f"/projects/{unrelated_id}").json()["projects"][0]
    assert "tasks" not in unrelated


def test_one_project_can_hold_several_todos(api, create_project, create_todo, link_project_to_todo):
    project_id, first_todo, second_todo = create_project(), create_todo(), create_todo()

    link_project_to_todo(first_todo, project_id)
    link_project_to_todo(second_todo, project_id)

    todos = ids_in(api.get(project_tasks_path(project_id)), "todos")
    assert sorted(todos) == sorted([first_todo, second_todo])


@pytest.mark.parametrize("missing_project_id", [MISSING_ID, "abc"])
def test_unknown_project_id_returns_404_and_creates_no_link(api, create_todo, missing_project_id):
    todo_id = create_todo()

    response = api.post(todo_projects_path(todo_id), data={"id": missing_project_id})

    assert response.status_code == 404
    assert "errorMessages" in response.json()
    assert api.get(todo_projects_path(todo_id)).json() == {"projects": []}


def test_unknown_todo_returns_404_and_creates_no_link(api, create_project):
    project_id = create_project()

    response = api.post(todo_projects_path(MISSING_ID), data={"id": project_id})

    assert response.status_code == 404
    assert "errorMessages" in response.json()
    assert api.get(project_tasks_path(project_id)).json() == {"todos": []}
