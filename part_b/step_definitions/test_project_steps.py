

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
    / "projects"
)

scenarios(str(FEATURE_DIR / "create_project.feature"))
scenarios(str(FEATURE_DIR / "view_projects.feature"))
scenarios(str(FEATURE_DIR / "update_project.feature"))
scenarios(str(FEATURE_DIR / "retrieve_project.feature"))
# ============================================================
# Shared fixtures and helpers
# ============================================================

@pytest.fixture
def project_case():
    """Store test data and clean up created projects."""
    case = {
        "response": None,
        "created_ids": [],
        "project_id": None,
    }

    yield case

    for project_id in reversed(case["created_ids"]):
        response = requests.delete(
            f"{BASE_URL}/projects/{project_id}",
            timeout=5
        )

        assert response.status_code in (200, 204, 404), (
            f"Project cleanup failed: {response.status_code}"
        )


def get_project(project_id):
    """Retrieve a project by its ID."""
    response = requests.get(
        f"{BASE_URL}/projects/{project_id}",
        timeout=5
    )

    assert response.status_code == 200, response.text

    projects = response.json()["projects"]

    assert len(projects) == 1
    assert projects[0]["id"] == project_id

    return projects[0]


def create_project(project_case, payload):
    """Create a project and register it for cleanup."""
    response = requests.post(
        f"{BASE_URL}/projects",
        json=payload,
        timeout=5
    )

    project_case["response"] = response

    if response.status_code == 201:
        project_id = response.json()["id"]

        project_case["project_id"] = project_id
        project_case["created_ids"].append(project_id)


# ============================================================
# Shared Gherkin steps
# ============================================================

@given("the Project API is running")
def verify_project_api():
    """Fail if the Java REST API is not running."""
    try:
        response = requests.get(
            f"{BASE_URL}/projects",
            timeout=5
        )
        response.raise_for_status()
    except requests.RequestException as error:
        pytest.fail(f"Project API unavailable: {error}")


@then(
    parsers.parse(
        "the project response status should be {status:d}"
    )
)
def check_project_status(project_case, status):
    response = project_case["response"]

    assert response.status_code == status, response.text


# ============================================================
# P01 - Create Project
# ============================================================

# Normal Flow

@when(
    parsers.parse(
        'I create a project with title "{title}" '
        'and description "{description}"'
    )
)
def create_project_with_description(
    project_case, title, description
):
    create_project(
        project_case,
        {
            "title": title,
            "description": description
        }
    )


# Alternate Flow

@when(
    parsers.parse(
        'I create a project with only title "{title}"'
    )
)
def create_project_title_only(project_case, title):
    create_project(
        project_case,
        {"title": title}
    )


# Error Flow

@when(
    parsers.parse(
        'I attempt to create a project with title "{title}" '
        'and invalid completed value "{completed}"'
    )
)
def create_project_invalid_status(
    project_case, title, completed
):
    before_response = requests.get(
        f"{BASE_URL}/projects",
        timeout=5
    )

    before_response.raise_for_status()

    project_case["before_projects"] = (
        before_response.json()["projects"]
    )

    create_project(
        project_case,
        {
            "title": title,
            "completed": completed
        }
    )


# ============================================================
# Assertions
# ============================================================

@then(
    parsers.parse(
        'the created project should have title "{title}"'
    )
)
def verify_created_project_title(project_case, title):
    project_id = project_case["project_id"]

    assert project_id is not None

    project = get_project(project_id)

    assert project["title"] == title


@then(
    parsers.parse(
        'the created project should have description "{description}"'
    )
)
def verify_created_project_description(
    project_case, description
):
    project_id = project_case["project_id"]

    project = get_project(project_id)

    assert project["description"] == description


@then("the project collection should remain unchanged")
def verify_project_collection_unchanged(project_case):
    response = requests.get(
        f"{BASE_URL}/projects",
        timeout=5
    )

    response.raise_for_status()

    assert response.json()["projects"] == (
        project_case["before_projects"]
    ), "Invalid project creation changed the collection"

# ============================================================
# P02 - View Projects
# ============================================================

# Shared setup for project viewing

@given(parsers.parse('a project exists with title "{title}"'))
def given_project_exists(project_case, title):
    create_project(project_case, {"title": title})

    response = project_case["response"]
    assert response.status_code == 201, response.text


@given(parsers.parse('another project exists with title "{title}"'))
def given_another_project_exists(project_case, title):
    create_project(project_case, {"title": title})

    response = project_case["response"]
    assert response.status_code == 201, response.text


# Normal and Alternate Flows

@when("I request the project list")
def request_project_list(project_case):
    project_case["response"] = requests.get(
        f"{BASE_URL}/projects",
        timeout=5
    )


@then(
    parsers.parse(
        'the project list should contain title "{title}"'
    )
)
def verify_project_in_list(project_case, title):
    response = project_case["response"]

    assert response.status_code == 200, response.text

    projects = response.json()["projects"]

    # Verify a project created during this scenario
    # appears in the returned collection.
    created_ids = set(project_case["created_ids"])

    assert any(
        project["id"] in created_ids
        and project["title"] == title
        for project in projects
    ), f"Project '{title}' was not found in the list"


# Error Flow

@when(
    parsers.parse(
        "I request a project with ID {project_id:d}"
    )
)
def request_invalid_project(project_case, project_id):
    project_case["response"] = requests.get(
        f"{BASE_URL}/projects/{project_id}",
        timeout=5
    )


@then("no project should be returned")
def verify_no_project_returned(project_case):
    response = project_case["response"]

    assert response.status_code == 404, response.text

    data = response.json()

    # Todo Manager reports failed lookups through
    # an errorMessages response.
    assert "errorMessages" in data
    assert data["errorMessages"]

# ============================================================
# P03 - Update Project
# ============================================================

@given(
    parsers.parse(
        'a project exists with title "{title}" '
        'and description "{description}"'
    )
)
def given_project_with_description(
    project_case, title, description
):
    create_project(
        project_case,
        {"title": title, "description": description}
    )
    assert project_case["response"].status_code == 201


@when(
    parsers.parse('I rename the project to "{title}"')
)
def rename_project(project_case, title):
    project_id = project_case["project_id"]

    project_case["response"] = requests.post(
        f"{BASE_URL}/projects/{project_id}",
        json={"title": title},
        timeout=5
    )


@when(
    parsers.parse('I replace the project with title "{title}"')
)
def replace_project(project_case, title):
    project_id = project_case["project_id"]

    project_case["response"] = requests.put(
        f"{BASE_URL}/projects/{project_id}",
        json={"title": title},
        timeout=5
    )


@when(
    parsers.parse(
        'I update the project completed status to "{status}"'
    )
)
def update_invalid_completed_status(project_case, status):
    project_id = project_case["project_id"]

    project_case["original_project"] = get_project(
        project_id
    ).copy()

    project_case["response"] = requests.post(
        f"{BASE_URL}/projects/{project_id}",
        json={"completed": status},
        timeout=5
    )


@then(
    parsers.parse(
        'the updated project should have title "{title}"'
    )
)
def verify_updated_project_title(project_case, title):
    project = get_project(project_case["project_id"])

    assert project["title"] == title


@then("the updated project description should be empty")
def verify_empty_project_description(project_case):
    project = get_project(project_case["project_id"])

    assert project["description"] == ""


@then("the project should remain unchanged")
def verify_project_unchanged(project_case):
    project = get_project(project_case["project_id"])

    assert project == project_case["original_project"]

# ============================================================
# P04 - Retrieve Project by ID
# ============================================================

@when("I request the current project by ID")
def request_current_project_by_id(project_case):
    """Retrieve the project created during the scenario."""
    project_id = project_case["project_id"]

    project_case["response"] = requests.get(
        f"{BASE_URL}/projects/{project_id}",
        timeout=5
    )


# --------------------
# Normal Flow
# --------------------

@then(
    parsers.parse(
        'the retrieved project should have title "{title}"'
    )
)
def verify_retrieved_project_title(project_case, title):
    """Verify the returned project has the correct ID and title."""
    response = project_case["response"]

    assert response.status_code == 200, response.text

    projects = response.json()["projects"]

    assert len(projects) == 1, response.text

    project = projects[0]

    assert project["id"] == project_case["project_id"]
    assert project["title"] == title


@then(
    parsers.parse(
        'the retrieved project should have description "{description}"'
    )
)
def verify_retrieved_project_description(
    project_case, description
):
    """Verify the returned project description."""
    response = project_case["response"]

    assert response.status_code == 200, response.text

    projects = response.json()["projects"]

    assert len(projects) == 1
    assert projects[0]["description"] == description


# --------------------
# Alternate Flow
# --------------------

@then("the retrieved project should have an empty description")
def verify_retrieved_project_empty_description(project_case):
    """Verify a project created without a description."""
    response = project_case["response"]

    assert response.status_code == 200, response.text

    projects = response.json()["projects"]

    assert len(projects) == 1
    assert projects[0]["description"] == ""


# --------------------
# Error Flow
# --------------------

@given("the current project has been deleted")
def delete_current_project_during_setup(project_case):
    """Delete the project before attempting retrieval."""
    project_id = project_case["project_id"]

    response = requests.delete(
        f"{BASE_URL}/projects/{project_id}",
        timeout=5
    )

    assert response.status_code == 200, response.text


@then("the response should contain project error messages")
def verify_project_error_messages(project_case):
    """Verify the API returns an error rather than project data."""
    response = project_case["response"]

    assert response.status_code == 404, response.text

    data = response.json()

    assert "errorMessages" in data, response.text
    assert isinstance(data["errorMessages"], list)
    assert data["errorMessages"], "Expected non-empty error messages"
    assert "projects" not in data or not data["projects"]
