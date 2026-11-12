
import os
from pathlib import Path

import pytest
import requests
from pytest_bdd import given, when, then, parsers, scenarios


BASE_URL = os.getenv(
    "TODO_API_URL", "http://localhost:4567"
).rstrip("/")

FEATURE_DIR = (
    Path(__file__).resolve().parents[1]
    / "features"
    / "todos"
)

scenarios(str(FEATURE_DIR / "create_todo.feature"))
scenarios(str(FEATURE_DIR / "view_todo.feature"))
scenarios(str(FEATURE_DIR / "update_todo.feature"))

@pytest.fixture
def todo_case():
    """Store scenario information and clean up created todos."""
    case = {
        "response": None,
        "created_ids": [],
        "title": None,
    }

    yield case

    for todo_id in reversed(case["created_ids"]):
        response = requests.delete(
            f"{BASE_URL}/todos/{todo_id}",
            timeout=5,
        )
        assert response.status_code in (200, 204, 404), (
            f"Cleanup failed: {response.status_code}"
        )


@given("the Todo Manager API is running")
def verify_api_running():
    """Confirm the API is available before testing."""
    try:
        response = requests.get(
            f"{BASE_URL}/todos",
            timeout=5,
        )
        response.raise_for_status()
    except requests.RequestException as error:
        pytest.fail(f"Todo Manager API unavailable: {error}")


@when(parsers.parse('I create a todo with title "{title}"'))
def create_todo(todo_case, title):
    """Create a todo through the REST API."""
    todo_case["title"] = title

    response = requests.post(
        f"{BASE_URL}/todos",
        json={"title": title},
        timeout=5,
    )

    todo_case["response"] = response

    if response.status_code == 201:
        todo_case["created_ids"].append(
            response.json()["id"]
        )


@then(parsers.parse("the response status should be {status:d}"))
def check_status(todo_case, status):
    """Check the expected HTTP status."""
    assert todo_case["response"].status_code == status, (
        todo_case["response"].text
    )


@then(parsers.parse('the todo with title "{title}" should exist'))
def check_todo_exists(todo_case, title):
    """Verify that the created todo can be retrieved."""
    assert todo_case["created_ids"], "No todo ID was saved"

    todo_id = todo_case["created_ids"][-1]

    response = requests.get(
        f"{BASE_URL}/todos/{todo_id}",
        timeout=5,
    )

    assert response.status_code == 200, response.text

    todos = response.json()["todos"]

    assert len(todos) == 1
    assert todos[0]["id"] == todo_id
    assert todos[0]["title"] == title

@when(
    parsers.parse(
        'I create a todo with title "{title}" '
        'and description "{description}"'
    )
)
def create_todo_with_description(todo_case, title, description):
    response = requests.post(
        f"{BASE_URL}/todos",
        json={
            "title": title,
            "description": description
        },
        timeout=5
    )

    todo_case["response"] = response

    if response.status_code == 201:
        todo_case["created_ids"].append(response.json()["id"])


@then(
    parsers.parse(
        'the created todo should have description "{description}"'
    )
)
def check_todo_description(todo_case, description):
    todo_id = todo_case["created_ids"][-1]

    response = requests.get(
        f"{BASE_URL}/todos/{todo_id}",
        timeout=5
    )

    assert response.status_code == 200, response.text
    assert response.json()["todos"][0]["description"] == description


@when("I attempt to create a todo with an empty title")
def create_todo_with_empty_title(todo_case):
    before = requests.get(f"{BASE_URL}/todos", timeout=5)
    before.raise_for_status()

    todo_case["before_ids"] = {
        todo["id"] for todo in before.json()["todos"]
    }

    response = requests.post(
        f"{BASE_URL}/todos",
        json={"title": ""},
        timeout=5
    )

    todo_case["response"] = response

    # Track even unexpectedly created objects for cleanup.
    if 200 <= response.status_code < 300:
        todo_case["created_ids"].append(response.json()["id"])


@then("the todo collection should remain unchanged")
def verify_todo_collection_unchanged(todo_case):
    response = requests.get(f"{BASE_URL}/todos", timeout=5)
    response.raise_for_status()

    after_ids = {
        todo["id"] for todo in response.json()["todos"]
    }

    assert after_ids == todo_case["before_ids"]

# ============================================================
# T02 - View Todo
# ============================================================

# Setup: Create a todo before testing retrieval
@given(parsers.parse('a todo exists with title "{title}"'))
def given_todo_exists(todo_case, title):
    response = requests.post(
        f"{BASE_URL}/todos",
        json={"title": title},
        timeout=5
    )

    assert response.status_code == 201, response.text

    todo_id = response.json()["id"]

    # Register the todo for automatic cleanup
    todo_case["created_ids"].append(todo_id)
    todo_case["todo_id"] = todo_id
    todo_case["title"] = title


# Normal Flow: Retrieve the created todo by ID
@when("I request the todo by its ID")
def request_todo_by_id(todo_case):
    todo_id = todo_case["todo_id"]

    todo_case["response"] = requests.get(
        f"{BASE_URL}/todos/{todo_id}",
        timeout=5
    )


# Alternate Flow: Retrieve the entire todo list
@when("I request the todo list")
def request_todo_list(todo_case):
    todo_case["response"] = requests.get(
        f"{BASE_URL}/todos",
        timeout=5
    )


# Error Flow: Retrieve a nonexistent todo
@when(parsers.parse("I request a todo with ID {todo_id:d}"))
def request_nonexistent_todo(todo_case, todo_id):
    todo_case["response"] = requests.get(
        f"{BASE_URL}/todos/{todo_id}",
        timeout=5
    )


# Verify normal flow
@then(
    parsers.parse(
        'the response should contain a todo with title "{title}"'
    )
)
def verify_todo_by_id(todo_case, title):
    response = todo_case["response"]

    assert response.status_code == 200, response.text

    todos = response.json()["todos"]

    assert len(todos) == 1
    assert todos[0]["id"] == todo_case["todo_id"]
    assert todos[0]["title"] == title


# Verify alternate flow
@then(
    parsers.parse(
        'the todo list should contain title "{title}"'
    )
)
def verify_todo_in_list(todo_case, title):
    response = todo_case["response"]

    assert response.status_code == 200, response.text

    todos = response.json()["todos"]

    assert any(
        todo["id"] == todo_case["todo_id"]
        and todo["title"] == title
        for todo in todos
    ), f"Created todo '{title}' not found in the list"

# ============================================================
# T03 - Update Todo
# ============================================================

def update_todo_field(todo_case, field, value):
    """Update one field of the current todo."""
    todo_id = todo_case["todo_id"]

    response = requests.post(
        f"{BASE_URL}/todos/{todo_id}",
        json={field: value},
        timeout=5
    )

    todo_case["response"] = response


def get_current_todo(todo_case):
    """Retrieve the todo after an update."""
    todo_id = todo_case["todo_id"]

    response = requests.get(
        f"{BASE_URL}/todos/{todo_id}",
        timeout=5
    )

    assert response.status_code == 200, response.text

    todos = response.json()["todos"]
    assert len(todos) == 1

    return todos[0]


# --------------------
# Normal Flow
# --------------------

@when(
    parsers.parse(
        'I update the todo title to "{new_title}"'
    )
)
def update_todo_title(todo_case, new_title):
    update_todo_field(
        todo_case,
        "title",
        new_title
    )


@then(
    parsers.parse(
        'the todo should have title "{title}"'
    )
)
def verify_updated_title(todo_case, title):
    todo = get_current_todo(todo_case)

    assert todo["title"] == title, (
        f"Expected title '{title}', "
        f"but got '{todo['title']}'"
    )


# --------------------
# Alternate Flow
# --------------------

@when(
    parsers.parse(
        'I update the todo description to "{description}"'
    )
)
def update_todo_description(todo_case, description):
    update_todo_field(
        todo_case,
        "description",
        description
    )


@then(
    parsers.parse(
        'the todo should have description "{description}"'
    )
)
def verify_updated_description(todo_case, description):
    todo = get_current_todo(todo_case)

    assert todo["description"] == description


@then(
    parsers.parse(
        'the todo title should remain "{title}"'
    )
)
def verify_title_unchanged(todo_case, title):
    todo = get_current_todo(todo_case)

    assert todo["title"] == title, (
        "Updating the description unexpectedly "
        "changed the todo title"
    )


# --------------------
# Error Flow
# --------------------

@when("I update the todo title to an empty string")
def update_todo_with_empty_title(todo_case):
    # Save the original values before updating.
    todo_case["original_todo"] = get_current_todo(todo_case).copy()

    update_todo_field(
        todo_case,
        "title",
        ""
    )


@then(
    parsers.parse(
        'the todo should still have its original title "{title}"'
    )
)
def verify_original_todo_preserved(todo_case, title):
    todo = get_current_todo(todo_case)
    original = todo_case["original_todo"]

    assert original["title"] == title

    # Invalid updates must not modify the todo.
    assert todo == original, (
        "The invalid update changed the original todo"
    )
