
import os
from pathlib import Path

import pytest
import requests
from pytest_bdd import given, when, then, parsers, scenarios


# ============================================================
# Configuration and Feature Registration
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
scenarios(str(FEATURE_DIR / "link_todo_category.feature"))
scenarios(str(FEATURE_DIR / "view_project_todos.feature"))
scenarios(str(FEATURE_DIR / "view_todo_categories.feature"))
# ============================================================
# Shared API Helpers
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
    """Create a temporary Todo, Project, or Category."""
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


def link_category_to_todo(case, category_id):
    """Link a category to a Todo and track the relationship."""
    todo_id = case["todo_id"]

    response = send_request(
        "POST",
        f"/todos/{todo_id}/categories",
        json={"id": category_id}
    )

    case["response"] = response

    if response.status_code == 201:
        case["category_links"].append(
            (todo_id, category_id)
        )

    return response


# ============================================================
# Shared Fixture and Automatic Cleanup
# ============================================================

@pytest.fixture
def interoperability_case():
    """Track all test-created entities and relationships."""
    case = {
        "response": None,
        "project_id": None,
        "todo_id": None,
        "category_id": None,
        "second_category_id": None,
        "created_objects": [],
        "created_links": [],
        "category_links": [],
    }

    yield case

    # Remove Todo-Category relationships first.
    for todo_id, category_id in reversed(case["category_links"]):
        response = send_request(
            "DELETE",
            f"/todos/{todo_id}/categories/{category_id}"
        )

        assert response.status_code in (200, 204, 404), (
            f"Category relationship cleanup failed: "
            f"{response.status_code} {response.text}"
        )

    # Remove Todo-Project relationships.
    for project_id, todo_id in reversed(case["created_links"]):
        response = send_request(
            "DELETE",
            f"/projects/{project_id}/tasks/{todo_id}"
        )

        assert response.status_code in (200, 204, 404), (
            f"Project relationship cleanup failed: "
            f"{response.status_code} {response.text}"
        )

    # Delete all temporary entities in reverse creation order.
    for entity_type, entity_id in reversed(
        case["created_objects"]
    ):
        response = send_request(
            "DELETE",
            f"/{entity_type}/{entity_id}"
        )

        assert response.status_code in (200, 204, 404), (
            f"Object cleanup failed for {entity_type}/{entity_id}: "
            f"{response.status_code} {response.text}"
        )


# ============================================================
# Background: Check API Availability
# ============================================================

@given("the Interoperability API is running")
def verify_interoperability_api():
    """Fail the test if the Todo Manager service is unavailable."""
    try:
        response = send_request(
            "GET",
            "/projects"
        )

        response.raise_for_status()

    except requests.RequestException as error:
        pytest.fail(
            f"Todo Manager API unavailable: {error}"
        )


# ============================================================
# Shared Gherkin Steps
# ============================================================

@given(parsers.parse('a project named "{title}" exists'))
def given_project_exists(interoperability_case, title):
    project_id = create_entity(
        interoperability_case,
        "projects",
        title
    )

    interoperability_case["project_id"] = project_id


@given(parsers.parse('a todo named "{title}" exists'))
def given_todo_exists(interoperability_case, title):
    todo_id = create_entity(
        interoperability_case,
        "todos",
        title
    )

    interoperability_case["todo_id"] = todo_id


@given(parsers.parse('a category named "{title}" exists'))
def given_category_exists(interoperability_case, title):
    category_id = create_entity(
        interoperability_case,
        "categories",
        title
    )

    interoperability_case["category_id"] = category_id


@given(
    parsers.parse(
        'another category named "{title}" exists'
    )
)
def given_second_category_exists(interoperability_case, title):
    category_id = create_entity(
        interoperability_case,
        "categories",
        title
    )

    interoperability_case["second_category_id"] = category_id


@then(
    parsers.parse(
        "the interoperability response status should be {status:d}"
    )
)
def verify_response_status(interoperability_case, status):
    """Verify the expected HTTP response status."""
    response = interoperability_case["response"]

    assert response is not None, "No API response was recorded"

    assert response.status_code == status, (
        f"Expected HTTP {status}, "
        f"received {response.status_code}: {response.text}"
    )


# ============================================================
# I01 - Link Todo to Project
# ============================================================

# --------------------
# Normal Flow
# --------------------

@when("I link the todo to the project")
def link_todo_to_project(interoperability_case):
    """Link an existing Todo through the Project endpoint."""
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


# --------------------
# Alternate Flow
# --------------------

@when("I link the project through the todo endpoint")
def link_project_through_todo(interoperability_case):
    """Link a Project through the Todo endpoint."""
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


# --------------------
# Error Flow
# --------------------

@when(
    parsers.parse(
        'I try to link a todo with invalid ID "{invalid_id}"'
    )
)
def link_invalid_todo(interoperability_case, invalid_id):
    """Attempt to link a nonexistent Todo to a Project."""
    project_id = interoperability_case["project_id"]

    interoperability_case["response"] = send_request(
        "POST",
        f"/projects/{project_id}/tasks",
        json={"id": invalid_id}
    )


# --------------------
# I01 Assertions
# --------------------

@then("the project should contain the linked todo")
def verify_project_contains_todo(interoperability_case):
    """Verify the relationship from the Project side."""
    project_id = interoperability_case["project_id"]
    todo_id = interoperability_case["todo_id"]

    linked_ids = get_linked_ids(
        f"/projects/{project_id}/tasks",
        "todos"
    )

    assert todo_id in linked_ids, (
        f"Todo {todo_id} is missing from Project {project_id}"
    )


@then("the todo should belong to the project")
def verify_todo_belongs_to_project(interoperability_case):
    """Verify the relationship from the Todo side."""
    project_id = interoperability_case["project_id"]
    todo_id = interoperability_case["todo_id"]

    linked_ids = get_linked_ids(
        f"/todos/{todo_id}/tasksof",
        "projects"
    )

    assert project_id in linked_ids, (
        f"Project {project_id} is missing from Todo {todo_id}"
    )


@then("the project should have no linked todos")
def verify_no_linked_todos(interoperability_case):
    """Verify an invalid request created no relationship."""
    project_id = interoperability_case["project_id"]

    linked_ids = get_linked_ids(
        f"/projects/{project_id}/tasks",
        "todos"
    )

    assert linked_ids == [], (
        "Invalid relationship request unexpectedly "
        "created a Project-Todo link"
    )


# ============================================================
# I02 - Link Todo to Category
# ============================================================

# --------------------
# Normal Flow
# --------------------

@when("I link the category to the todo")
def link_single_category(interoperability_case):
    """Assign one Category to the current Todo."""
    category_id = interoperability_case["category_id"]

    link_category_to_todo(
        interoperability_case,
        category_id
    )


@then("the todo should contain the linked category")
def verify_linked_category(interoperability_case):
    """Verify the assigned Category exists on the Todo."""
    todo_id = interoperability_case["todo_id"]
    category_id = interoperability_case["category_id"]

    linked_ids = get_linked_ids(
        f"/todos/{todo_id}/categories",
        "categories"
    )

    assert category_id in linked_ids, (
        f"Category {category_id} was not linked to Todo {todo_id}"
    )


# --------------------
# Alternate Flow
# --------------------

@when("I link both categories to the todo")
def link_two_categories(interoperability_case):
    """Assign two different Categories to one Todo."""
    first_id = interoperability_case["category_id"]
    second_id = interoperability_case["second_category_id"]

    first_response = link_category_to_todo(
        interoperability_case,
        first_id
    )

    assert first_response.status_code == 201, (
        first_response.text
    )

    second_response = link_category_to_todo(
        interoperability_case,
        second_id
    )

    assert second_response.status_code == 201, (
        second_response.text
    )


@then("the todo should contain both linked categories")
def verify_both_categories(interoperability_case):
    """Verify both Categories are assigned to the Todo."""
    todo_id = interoperability_case["todo_id"]

    expected_ids = {
        interoperability_case["category_id"],
        interoperability_case["second_category_id"]
    }

    linked_ids = get_linked_ids(
        f"/todos/{todo_id}/categories",
        "categories"
    )

    assert set(linked_ids) == expected_ids, (
        f"Expected categories {expected_ids}, "
        f"but received {set(linked_ids)}"
    )


# --------------------
# Error Flow
# --------------------

@when(
    parsers.parse(
        'I try to link a category with invalid ID "{invalid_id}"'
    )
)
def link_invalid_category(interoperability_case, invalid_id):
    """Attempt to assign a nonexistent Category."""
    todo_id = interoperability_case["todo_id"]

    interoperability_case["response"] = send_request(
        "POST",
        f"/todos/{todo_id}/categories",
        json={"id": invalid_id}
    )


@then("the todo should have no linked categories")
def verify_no_linked_categories(interoperability_case):
    """Verify an invalid Category assignment creates no link."""
    todo_id = interoperability_case["todo_id"]

    linked_ids = get_linked_ids(
        f"/todos/{todo_id}/categories",
        "categories"
    )

    assert linked_ids == [], (
        "Invalid category request unexpectedly "
        "created a Todo-Category relationship"
    )

# ============================================================
# I03 - View Project Todos
# ============================================================

def create_project_todo_link(case, todo_id):
    """Link a Todo to the current Project for test setup."""
    project_id = case["project_id"]

    response = send_request(
        "POST",
        f"/projects/{project_id}/tasks",
        json={"id": todo_id}
    )

    assert response.status_code == 201, response.text

    case["created_links"].append(
        (project_id, todo_id)
    )


# --------------------
# Setup
# --------------------

@given("the todo is linked to the project")
def given_todo_is_linked_to_project(interoperability_case):
    todo_id = interoperability_case["todo_id"]

    create_project_todo_link(
        interoperability_case,
        todo_id
    )


@given(
    parsers.parse(
        'another todo named "{title}" exists'
    )
)
def given_second_todo_exists(interoperability_case, title):
    todo_id = create_entity(
        interoperability_case,
        "todos",
        title
    )

    interoperability_case["second_todo_id"] = todo_id


@given("both todos are linked to the project")
def given_both_todos_are_linked(interoperability_case):
    first_id = interoperability_case["todo_id"]
    second_id = interoperability_case["second_todo_id"]

    create_project_todo_link(
        interoperability_case,
        first_id
    )

    create_project_todo_link(
        interoperability_case,
        second_id
    )


# --------------------
# Normal and Alternate Flows
# --------------------

@when("I request the todos belonging to the project")
def request_project_todos(interoperability_case):
    project_id = interoperability_case["project_id"]

    interoperability_case["response"] = send_request(
        "GET",
        f"/projects/{project_id}/tasks"
    )


@then("the project todo list should contain the linked todo")
def verify_project_todo_list(interoperability_case):
    response = interoperability_case["response"]

    todos = response.json()["todos"]

    actual_ids = {
        todo["id"]
        for todo in todos
    }

    expected_id = interoperability_case["todo_id"]

    assert actual_ids == {expected_id}, (
        f"Expected Todo {expected_id}, "
        f"but received {actual_ids}"
    )


@then("the project todo list should contain both linked todos")
def verify_project_two_todos(interoperability_case):
    response = interoperability_case["response"]

    todos = response.json()["todos"]

    actual_ids = {
        todo["id"]
        for todo in todos
    }

    expected_ids = {
        interoperability_case["todo_id"],
        interoperability_case["second_todo_id"]
    }

    assert actual_ids == expected_ids, (
        f"Expected Todos {expected_ids}, "
        f"but received {actual_ids}"
    )



# --------------------
# Error Flow
# --------------------

@when(
    parsers.parse(
        'I request the project todos with unsupported Accept "{media_type}"'
    )
)
def request_project_todos_unsupported_format(
    interoperability_case, media_type
):
    project_id = interoperability_case["project_id"]

    interoperability_case["response"] = send_request(
        "GET",
        f"/projects/{project_id}/tasks",
        headers={"Accept": media_type}
    )
    
# ============================================================
# I04 - View Todo Categories
# ============================================================

# --------------------
# Setup
# --------------------

@given("the category is linked to the todo")
def given_category_is_linked_to_todo(interoperability_case):
    """Create one Todo-Category link before retrieval."""
    category_id = interoperability_case["category_id"]

    response = link_category_to_todo(
        interoperability_case,
        category_id
    )

    assert response.status_code == 201, response.text


@given("both categories are linked to the todo")
def given_both_categories_are_linked(interoperability_case):
    """Create two Todo-Category links before retrieval."""
    first_id = interoperability_case["category_id"]
    second_id = interoperability_case["second_category_id"]

    first_response = link_category_to_todo(
        interoperability_case,
        first_id
    )

    assert first_response.status_code == 201, (
        first_response.text
    )

    second_response = link_category_to_todo(
        interoperability_case,
        second_id
    )

    assert second_response.status_code == 201, (
        second_response.text
    )


# --------------------
# Normal and Alternate Flows
# --------------------

@when("I request the categories belonging to the todo")
def request_todo_categories(interoperability_case):
    """GET the categories belonging to the current Todo."""
    todo_id = interoperability_case["todo_id"]

    interoperability_case["response"] = send_request(
        "GET",
        f"/todos/{todo_id}/categories"
    )


@then("the todo category list should contain the linked category")
def verify_todo_category_list(interoperability_case):
    """Verify exactly one expected Category is returned."""
    response = interoperability_case["response"]

    assert response.status_code == 200, response.text

    categories = response.json()["categories"]

    actual_ids = {
        category["id"]
        for category in categories
    }

    expected_id = interoperability_case["category_id"]

    assert actual_ids == {expected_id}, (
        f"Expected Category {expected_id}, "
        f"but received {actual_ids}"
    )


@then("the todo category list should contain both linked categories")
def verify_todo_two_categories(interoperability_case):
    """Verify both assigned Categories are returned."""
    response = interoperability_case["response"]

    assert response.status_code == 200, response.text

    categories = response.json()["categories"]

    actual_ids = {
        category["id"]
        for category in categories
    }

    expected_ids = {
        interoperability_case["category_id"],
        interoperability_case["second_category_id"]
    }

    assert actual_ids == expected_ids, (
        f"Expected Categories {expected_ids}, "
        f"but received {actual_ids}"
    )


# --------------------
# Error Flow
# --------------------

@when(
    parsers.parse(
        'I request the todo categories with unsupported Accept "{media_type}"'
    )
)
def request_todo_categories_unsupported_format(
    interoperability_case, media_type
):
    """Request a response format not supported by the API."""
    todo_id = interoperability_case["todo_id"]

    interoperability_case["response"] = send_request(
        "GET",
        f"/todos/{todo_id}/categories",
        headers={"Accept": media_type}
    )
