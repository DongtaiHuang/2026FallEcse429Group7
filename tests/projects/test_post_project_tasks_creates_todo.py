"""API under test: POST /projects/:id/tasks with todo fields instead of an id (undocumented).

Besides linking an existing todo, the endpoint creates a brand-new todo that is already linked.
"""
import pytest

from task_link_support import JSON, XML, ids_in, project_tasks_path, send_raw, xml_root

pytestmark = pytest.mark.undocumented


def test_creates_a_linked_todo_and_returns_it(api, create_project, state):
    project_id = create_project()

    response = api.post(project_tasks_path(project_id), data={"title": "Draft launch email", "description": "Send on Monday"})
    state.track_created("todos", response.json()["id"])

    todo = response.json()
    assert response.status_code == 201
    assert (todo["title"], todo["description"], todo["doneStatus"]) == ("Draft launch email", "Send on Monday", "false")
    assert todo["tasksof"] == [{"id": project_id}]


def test_new_todo_is_retrievable_on_its_own(api, create_project, state):
    project_id = create_project()
    created = api.post(project_tasks_path(project_id), data={"title": "Draft launch email"}).json()
    state.track_created("todos", created["id"])

    response = api.get(f"/todos/{created['id']}")

    assert response.status_code == 200
    assert response.json()["todos"][0]["title"] == "Draft launch email"


def test_new_todo_is_listed_by_the_project(api, create_project, state):
    project_id = create_project()
    created = api.post(project_tasks_path(project_id), data={"title": "Draft launch email"}).json()
    state.track_created("todos", created["id"])

    assert ids_in(api.get(project_tasks_path(project_id)), "todos") == [created["id"]]


def test_creates_a_linked_todo_from_an_xml_body(api, create_project, state):
    project_id = create_project()

    response = send_raw(api, "POST", project_tasks_path(project_id), body="<todo><title>Book the venue</title></todo>",
                        content_type=XML, accept=XML)
    todo_id = xml_root(response).findtext("id")
    state.track_created("todos", todo_id)

    assert response.status_code == 201
    assert response.headers["Content-Type"].startswith(XML)
    assert xml_root(response).findtext("title") == "Book the venue"
    assert ids_in(api.get(project_tasks_path(project_id)), "todos") == [todo_id]


def test_empty_title_is_rejected_and_creates_no_todo(api, create_project):
    project_id = create_project()

    response = api.post(project_tasks_path(project_id), data={"title": ""})

    assert response.status_code == 400
    assert response.headers["Content-Type"].startswith(JSON)
    assert api.get(project_tasks_path(project_id)).json() == {"todos": []}


def test_body_without_id_or_title_is_rejected_as_a_missing_todo_title(api, create_project):
    """Current behaviour: the message talks about a todo title because the body is treated as a new todo."""
    project_id = create_project()

    response = api.post(project_tasks_path(project_id), data={})

    assert response.status_code == 400
    assert response.json()["errorMessages"] == ["title : field is mandatory"]
