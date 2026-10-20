"""Fixtures for the project-todo link modules.

Every test in this folder automatically gets the same lifecycle:
  1. ensure the system is ready   -> service_must_be_running   (fails the test if the app is down)
  2. save the system state        -> system_state_is_restored  (snapshot before the test)
  3. set up initial conditions    -> create_todo / create_project / link_todo_to_project
  4. execute and assess           -> the test body
  5. restore the initial state    -> StateManager.restore(), then compare with the snapshot

Needs the team's root conftest fixtures `api` and `state_manager`.
"""
import os
import sys
import uuid

import pytest
import requests

sys.path.insert(0, os.path.dirname(__file__))

from task_link_support import project_tasks_path, snapshot  # noqa: E402


def pytest_configure(config):
    config.addinivalue_line("markers", "documented: API operation described in /docs or swagger")
    config.addinivalue_line("markers", "undocumented: behaviour found by exploration, absent from the docs")
    config.addinivalue_line("markers", "bug_expected: documented/expected behaviour; FAILS today because of a bug")
    config.addinivalue_line("markers", "default_data: relies on the application's startup data (fresh server)")
    config.addinivalue_line("markers", "bug_actual: records the behaviour the app really has; PASSES today")


@pytest.fixture(autouse=True)
def service_must_be_running(api):
    """Fail (not skip) every test when the Todo Manager cannot be reached."""
    try:
        api.get("/todos")
    except requests.RequestException as error:
        pytest.fail(f"Todo Manager is not running at {api.base_url}: {error}", pytrace=False)


@pytest.fixture(autouse=True)
def system_state_is_restored(api, service_must_be_running):
    """Save the todos, projects and categories before a test and prove they are identical afterwards."""
    before = snapshot(api)
    yield
    assert snapshot(api) == before, "the test left data behind or changed existing data"


@pytest.fixture
def state(state_manager):
    """The team's StateManager fixture: its undo actions run when the test ends, even if it failed."""
    return state_manager


@pytest.fixture
def create_todo(api, state):
    def create(**fields):
        payload = {"title": f"links-todo-{uuid.uuid4().hex[:8]}", **fields}
        response = api.post("/todos", data=payload)
        assert response.status_code == 201, response.text
        todo_id = response.json()["id"]
        state.track_created("todos", todo_id)
        return todo_id

    return create


@pytest.fixture
def create_project(api, state):
    def create(**fields):
        payload = {"title": f"links-project-{uuid.uuid4().hex[:8]}", **fields}
        response = api.post("/projects", data=payload)
        assert response.status_code == 201, response.text
        project_id = response.json()["id"]
        state.track_created("projects", project_id)
        return project_id

    return create


@pytest.fixture
def link_todo_to_project(api, state):
    """Arrange step: link through the documented project-side call and register the undo."""

    def link(project_id, todo_id):
        response = api.post(project_tasks_path(project_id), data={"id": todo_id})
        assert response.status_code == 201, response.text
        state.track_relationship("projects", project_id, "tasks", todo_id)

    return link
