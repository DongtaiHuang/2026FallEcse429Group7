

import os
from pathlib import Path

import pytest
import requests
from pytest_bdd import given, when, then, parsers, scenarios


# ============================================================
# Configuration
# ============================================================

BASE_URL = os.getenv(
    "TODO_API_URL", "http://localhost:4567"
).rstrip("/")

FEATURE_DIR = (
    Path(__file__).resolve().parents[1]
    / "features"
    / "interoperability"
)

scenarios(str(FEATURE_DIR / "link_todo_project.feature"))


# ============================================================
# Shared helpers
# ============================================================

def send_request(method, endpoint, **kwargs):
    """Send an HTTP request to the REST API."""
    return requests.request(
        method,
        f"{BASE_URL}{endpoint}",
        timeout=5,
        **kwargs
    )


def create_entity(case, entity_type, title):
    """Create a temporary Todo or Project."""
    response = send_request(
        "POST",
        f"/{entity_type}",
        json={"title": title}
    )

    assert response.status_code == 201, response.text

    entity_id = response.json()["id"]

    case["created_objects"].append(
        (entity_type, entity_id)
    )

    return entity_id


def get_linked_ids(endpoint, collection):
    """Retrieve IDs from a relationship endpoint."""
    response = send_request("GET", endpoint)

    assert response.status_code == 200, response.text

    return [
        item["id"]
        for item in response.json()[collection]
    ]


# ============================================================
# Shared fixture and cleanup
# ============================================================

@pytest.fixture
def interoperability_case():
    """Track created objects and relationships."""
    case = {
        "response": None,
        "project_id": None,
        "todo_id": None,
        "created_objects": [],
        "created_links": []
    }

    yield case

    # Remove links before deleting objects.
    for project_id, todo_id in reversed(case["created_links"]):
        response = send_request(
            "DELETE",
            f"/projects/{project_id}/tasks/{todo_id}"
        )

        assert response.status_code in (200, 204, 404), (
            f"Relationship cleanup failed: {response.text}"
        )

    # Delete temporary Todos and Projects.
    for entity_type, entity_id in reversed(case["created_objects"]):
        response = send_request(
            "DELETE",
            f"/{entity_type}/{entity_id}"
        )

        assert response.status_code in (200, 204, 404), (
            f"Object cleanup failed: {response.text}"
        )


# ============================================================
# Background
# ============================================================

@given("the Interoperability API is running")
def verify_interoperability_api():
    """Fail if the service is unavailable."""
    try:
        response = send_request("GET", "/projects")
        response.raise_for_status()
    except requests.RequestException as error:
        pytest.fail(
            f"Todo Manager API unavailable: {error}"
        )


# ============================================================
# I01 - Link Todo to Project
# ============================================================

@given(parsers.parse('a project named "{title}" exists'))
def given_project_exists(interoperability_case, title):
    project_id = create_entity(
        interoperability_case, "projects", title
    )
    interoperability_case["project_id"] = project_id


@given(parsers.parse('a todo named "{title}" exists'))
def given_todo_exists(interoperability_case, title):
    todo_id = create_entity(
        interoperability_case, "todos", title
    )
    interoperability_case["todo_id"] = todo_id


# Normal Flow
@when("I link the todo to the project")
def link_todo_to_project(interoperability_case):
    project_id = interoperability_case["project_id"]
    todo_id = interoperability_case["todo_id"]

    response = send_request(
        "POST",
        f"/projects/{project_id}/tasks",
        json={"id": todo_id}
    )

    interoperability_case["response"] = response

    if response.status_code == 201:
        interoperability_case["created_links"].append(
            (project_id, todo_id)
        )


# Alternate Flow
@when("I link the project through the todo endpoint")
def link_project_through_todo(interoperability_case):
    project_id = interoperability_case["project_id"]
    todo_id = interoperability_case["todo_id"]

    response = send_request(
        "POST",
        f"/todos/{todo_id}/tasksof",
        json={"id": project_id}
    )

    interoperability_case["response"] = response

    if response.status_code == 201:
        interoperability_case["created_links"].append(
            (project_id, todo_id)
        )


# Error Flow
@when(
    parsers.parse(
        'I try to link a todo with invalid ID "{invalid_id}"'
    )
)
def link_invalid_todo(interoperability_case, invalid_id):
    project_id = interoperability_case["project_id"]

    interoperability_case["response"] = send_request(
        "POST",
        f"/projects/{project_id}/tasks",
        json={"id": invalid_id}
    )


# ============================================================
# Reusable assertions
# ============================================================

@then(
    parsers.parse(
        "the interoperability response status should be {status:d}"
    )
)
def verify_response_status(interoperability_case, status):
    response = interoperability_case["response"]
    assert response.status_code == status, response.text


@then("the project should contain the linked todo")
def verify_project_contains_todo(interoperability_case):
    project_id = interoperability_case["project_id"]
    todo_id = interoperability_case["todo_id"]

    linked_ids = get_linked_ids(
        f"/projects/{project_id}/tasks",
        "todos"
    )

    assert todo_id in linked_ids


@then("the todo should belong to the project")
def verify_todo_belongs_to_project(interoperability_case):
    project_id = interoperability_case["project_id"]
    todo_id = interoperability_case["todo_id"]

    linked_ids = get_linked_ids(
        f"/todos/{todo_id}/tasksof",
        "projects"
    )

    assert project_id in linked_ids


@then("the project should have no linked todos")
def verify_no_linked_todos(interoperability_case):
    project_id = interoperability_case["project_id"]

    linked_ids = get_linked_ids(
        f"/projects/{project_id}/tasks",
        "todos"
    )

    assert linked_ids == []
