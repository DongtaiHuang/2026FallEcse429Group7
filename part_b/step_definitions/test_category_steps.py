
import os
from pathlib import Path

import pytest
import requests
from pytest_bdd import given, parsers, scenarios, then, when


# ============================================================
# Configuration and feature registrations
# ============================================================

BASE_URL = os.getenv(
    "TODO_API_URL", "http://localhost:4567"
).rstrip("/")

FEATURE_DIR = (
    Path(__file__).resolve().parents[1]
    / "features"
    / "category"
)

scenarios(str(FEATURE_DIR / "create_category.feature"))
scenarios(str(FEATURE_DIR / "view_categories.feature"))
scenarios(str(FEATURE_DIR / "update_category.feature"))
scenarios(str(FEATURE_DIR / "retrieve_category.feature"))
scenarios(str(FEATURE_DIR / "delete_category.feature"))


# ============================================================
# Shared helpers
# ============================================================

def send(case, method, path, **kwargs):
    """Send a request through the scenario's HTTP session."""
    return case["client"].request(
        method,
        f"{BASE_URL}{path}",
        timeout=5,
        **kwargs
    )


def category_snapshot(response):
    """Return the category collection indexed by ID."""
    assert response.status_code == 200, response.text

    return {
        category["id"]: category
        for category in response.json()["categories"]
    }


def create_category(case, payload):
    """Create a category and track it for cleanup."""
    response = send(
        case,
        "POST",
        "/categories",
        json=payload
    )

    case["response"] = response

    if 200 <= response.status_code < 300:
        category_id = response.json()["id"]

        case["created_ids"].append(category_id)
        case["category_id"] = category_id


def get_saved_category(case):
    """Retrieve the category most recently created."""
    category_id = case["category_id"]

    response = send(
        case,
        "GET",
        f"/categories/{category_id}"
    )

    assert response.status_code == 200, response.text

    categories = category_snapshot(response)

    assert category_id in categories, response.text

    return categories[category_id]


def check_saved_category(case, title, description):
    """Verify the persisted title and description."""
    category = get_saved_category(case)

    assert category["title"] == title
    assert category["description"] == description


def update_saved_category(case, changes):
    """Partially update the most recently created category."""
    category_id = case["category_id"]

    case["response"] = send(
        case,
        "POST",
        f"/categories/{category_id}",
        json=changes
    )


# ============================================================
# Shared fixture: test isolation and cleanup
# ============================================================

@pytest.fixture
def category_case():
    """Track temporary categories and clean up after each test."""
    with requests.Session() as client:
        client.headers["Accept"] = "application/json"

        case = {
            "client": client,
            "response": None,
            "created_ids": [],
            "category_id": None,
        }

        yield case

        # Delete only objects created by this scenario.
        for category_id in reversed(case["created_ids"]):
            response = send(
                case,
                "DELETE",
                f"/categories/{category_id}"
            )

            assert response.status_code in (200, 204, 404), (
                f"Category cleanup failed for {category_id}: "
                f"{response.status_code} {response.text}"
            )

        # Verify the original collection has been restored.
        if "before" in case:
            response = send(case, "GET", "/categories")
            after = category_snapshot(response)

            assert after == case["before"], (
                "Category collection was not restored "
                "after the scenario"
            )


# ============================================================
# Shared Background steps
# ============================================================

@given("the Todo Manager API is running")
def verify_api_is_running(category_case):
    """Fail when the Todo Manager REST API is unavailable."""
    try:
        response = send(
            category_case,
            "GET",
            "/categories"
        )
        response.raise_for_status()

    except requests.RequestException as error:
        pytest.fail(
            f"Todo Manager API unavailable at {BASE_URL}: {error}"
        )

    category_case["initial_response"] = response


@given("I have recorded the current category collection")
def record_category_collection(category_case):
    """Save the collection before the scenario."""
    category_case["before"] = category_snapshot(
        category_case["initial_response"]
    )


# ============================================================
# Shared Then steps
# ============================================================

@then(
    parsers.parse(
        "the response status should be {status:d}"
    )
)
def check_response_status(category_case, status):
    response = category_case["response"]

    assert response.status_code == status, response.text


@then(
    parsers.parse(
        'the saved category should have title "{title}" '
        'and description "{description}"'
    )
)
def check_saved_category_fields(
    category_case, title, description
):
    check_saved_category(
        category_case,
        title,
        description
    )


@then(
    parsers.parse(
        'the saved category should have title "{title}" '
        'and an empty description'
    )
)
def check_saved_category_has_empty_description(
    category_case, title
):
    check_saved_category(category_case, title, "")


@then("the category collection should be unchanged")
def check_category_collection_is_unchanged(category_case):
    response = send(
        category_case,
        "GET",
        "/categories"
    )

    assert category_snapshot(response) == category_case["before"]


# ============================================================
# C01 - Create Category
# ============================================================

@when(
    parsers.parse(
        'I create a category with title "{title}" '
        'and description "{description}"'
    )
)
def create_category_with_title_and_description(
    category_case, title, description
):
    create_category(
        category_case,
        {
            "title": title,
            "description": description
        }
    )


@when(
    parsers.parse(
        'I create a category with only the title "{title}"'
    )
)
def create_category_with_title_only(category_case, title):
    create_category(
        category_case,
        {"title": title}
    )


@when(
    parsers.parse(
        'I try to create a category with an empty title '
        'and description "{description}"'
    )
)
def create_category_with_empty_title(
    category_case, description
):
    create_category(
        category_case,
        {
            "title": "",
            "description": description
        }
    )


# ============================================================
# C02 - View Categories
# ============================================================

@given(
    parsers.parse(
        'I have created a category named "{title}"'
    )
)
def create_list_fixture(category_case, title):
    create_category(
        category_case,
        {"title": title}
    )

    response = category_case["response"]

    assert response.status_code == 201, response.text


@when("I request the category list")
def request_category_list(category_case):
    category_case["response"] = send(
        category_case,
        "GET",
        "/categories"
    )


@when(
    parsers.parse(
        'I request categories with title "{title}"'
    )
)
def request_categories_by_title(category_case, title):
    category_case["response"] = send(
        category_case,
        "GET",
        "/categories",
        params={"title": title}
    )


@when(
    parsers.parse(
        'I request the category list with Accept "{media_type}"'
    )
)
def request_category_list_with_accept(
    category_case, media_type
):
    category_case["response"] = send(
        category_case,
        "GET",
        "/categories",
        headers={"Accept": media_type}
    )


@then("the category list should include the category I last created")
def check_list_includes_created_category(category_case):
    response = category_case["response"]

    categories = category_snapshot(response)

    assert category_case["category_id"] in categories, (
        response.text
    )


@then(
    parsers.parse(
        'every returned category should have title "{title}"'
    )
)
def check_returned_category_titles(category_case, title):
    response = category_case["response"]

    categories = category_snapshot(response)

    assert categories, response.text

    assert all(
        category["title"] == title
        for category in categories.values()
    )


# ============================================================
# C03 - Update Category
# ============================================================

@given(
    parsers.parse(
        'I have created a category with title "{title}" '
        'and description "{description}"'
    )
)
def create_category_fixture_with_description(
    category_case, title, description
):
    create_category(
        category_case,
        {
            "title": title,
            "description": description
        }
    )

    response = category_case["response"]

    assert response.status_code == 201, response.text


@when(
    parsers.parse(
        'I rename the saved category to "{title}"'
    )
)
def rename_saved_category(category_case, title):
    update_saved_category(
        category_case,
        {"title": title}
    )


@when(
    parsers.parse(
        'I change the saved category description to "{description}"'
    )
)
def change_saved_category_description(
    category_case, description
):
    update_saved_category(
        category_case,
        {"description": description}
    )


@when("I try to rename the saved category to an empty title")
def rename_saved_category_to_empty_title(category_case):
    update_saved_category(
        category_case,
        {"title": ""}
    )


# ============================================================
# C04 - Retrieve Category by ID
# ============================================================

@given("the category I last created has been deleted")
def delete_category_before_retrieval(category_case):
    category_id = category_case["category_id"]

    response = send(
        category_case,
        "DELETE",
        f"/categories/{category_id}"
    )

    assert response.status_code == 200, response.text


@when("I request the category I last created by ID")
def request_category_by_id(category_case):
    category_id = category_case["category_id"]

    category_case["response"] = send(
        category_case,
        "GET",
        f"/categories/{category_id}"
    )


def check_retrieved_category(case, title, description):
    """Verify the response contains the requested category."""
    response = case["response"]

    assert response.status_code == 200, response.text

    categories = response.json()["categories"]

    assert len(categories) == 1, response.text

    category = categories[0]

    assert category["id"] == case["category_id"]
    assert category["title"] == title
    assert category["description"] == description


@then(
    parsers.parse(
        'the response should contain the requested category '
        'with title "{title}" and description "{description}"'
    )
)
def check_retrieved_category_fields(
    category_case, title, description
):
    check_retrieved_category(
        category_case,
        title,
        description
    )


@then(
    parsers.parse(
        'the response should contain the requested category '
        'with title "{title}" and an empty description'
    )
)
def check_retrieved_category_has_empty_description(
    category_case, title
):
    check_retrieved_category(
        category_case,
        title,
        ""
    )


# ============================================================
# C05 - Delete Category
# ============================================================

@when("I delete the category I last created")
def delete_last_created_category(category_case):
    category_id = category_case["category_id"]

    category_case["response"] = send(
        category_case,
        "DELETE",
        f"/categories/{category_id}"
    )


@then("the deleted category should no longer be retrievable")
def check_deleted_category_is_not_retrievable(category_case):
    category_id = category_case["category_id"]

    response = send(
        category_case,
        "GET",
        f"/categories/{category_id}"
    )

    assert response.status_code == 404, response.text


@then(
    parsers.parse(
        'the first category I created should still have title "{title}"'
    )
)
def check_first_category_was_preserved(category_case, title):
    category_id = category_case["created_ids"][0]

    response = send(
        category_case,
        "GET",
        f"/categories/{category_id}"
    )

    categories = category_snapshot(response)

    assert category_id in categories, response.text
    assert categories[category_id]["title"] == title
