"""API under test: query-string filters on GET /projects/:id/tasks and GET /todos/:id/tasksof (undocumented)."""
import pytest

from task_link_support import ids_in, project_tasks_path, todo_projects_path

pytestmark = pytest.mark.undocumented


@pytest.fixture
def project_with_open_and_done_todos(create_project, create_todo, link_todo_to_project):
    project_id = create_project(title="Website redesign")
    open_todo = create_todo(title="Write homepage copy", doneStatus=False)
    done_todo = create_todo(title="Pick a color palette", doneStatus=True)
    link_todo_to_project(project_id, open_todo)
    link_todo_to_project(project_id, done_todo)
    return project_id, open_todo, done_todo


def test_filter_by_done_status_true_returns_only_done_todos(api, project_with_open_and_done_todos):
    project_id, _, done_todo = project_with_open_and_done_todos

    response = api.get(project_tasks_path(project_id), params={"doneStatus": "true"})

    assert ids_in(response, "todos") == [done_todo]


def test_filter_by_done_status_false_returns_only_open_todos(api, project_with_open_and_done_todos):
    project_id, open_todo, _ = project_with_open_and_done_todos

    response = api.get(project_tasks_path(project_id), params={"doneStatus": "false"})

    assert ids_in(response, "todos") == [open_todo]


def test_filter_by_title_returns_the_matching_todo(api, project_with_open_and_done_todos):
    project_id, open_todo, _ = project_with_open_and_done_todos

    response = api.get(project_tasks_path(project_id), params={"title": "Write homepage copy"})

    assert ids_in(response, "todos") == [open_todo]


def test_filter_matching_nothing_returns_200_and_an_empty_list(api, project_with_open_and_done_todos):
    project_id, _, _ = project_with_open_and_done_todos

    response = api.get(project_tasks_path(project_id), params={"title": "no such title"})

    assert response.status_code == 200
    assert response.json() == {"todos": []}


def test_combined_filters_must_all_match(api, project_with_open_and_done_todos):
    project_id, _, done_todo = project_with_open_and_done_todos

    matching = api.get(project_tasks_path(project_id), params={"doneStatus": "true", "title": "Pick a color palette"})
    contradicting = api.get(project_tasks_path(project_id), params={"doneStatus": "false", "title": "Pick a color palette"})

    assert ids_in(matching, "todos") == [done_todo]
    assert ids_in(contradicting, "todos") == []


def test_filter_on_the_todo_side_by_project_title(api, create_project, create_todo, link_todo_to_project):
    project_id, todo_id = create_project(title="Website redesign"), create_todo()
    link_todo_to_project(project_id, todo_id)

    response = api.get(todo_projects_path(todo_id), params={"title": "Website redesign"})

    assert ids_in(response, "projects") == [project_id]


def test_filter_on_the_todo_side_excludes_non_matching_projects(api, create_project, create_todo, link_todo_to_project):
    project_id, todo_id = create_project(active=False), create_todo()
    link_todo_to_project(project_id, todo_id)

    response = api.get(todo_projects_path(todo_id), params={"active": "true"})

    assert ids_in(response, "projects") == []
