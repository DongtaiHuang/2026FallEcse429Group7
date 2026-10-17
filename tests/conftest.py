
import os

import pytest
import requests
from base.api_helper import APIHelper
from base.state_manager import StateManager
BASE_URL = os.getenv("TODO_API_URL", "http://localhost:4567")

@pytest.fixture
def api(api_url):
    """Provide a shared API helper for each test."""
    helper = APIHelper(base_url=api_url)

    yield helper

    helper.close()


@pytest.fixture(scope="session")
def api_url():
    """Return the base URL of the Todo Manager REST API."""
    return BASE_URL


@pytest.fixture(scope="session", autouse=True)
def check_service_running():
    """Verify that the API is available before running tests."""
    try:
        response = requests.get(
            f"{BASE_URL}/todos",
            timeout=5
        )
        response.raise_for_status()
    except requests.RequestException as error:
        pytest.fail(
            f"Todo Manager API is unavailable at {BASE_URL}: {error}",
            pytrace=False
        )


@pytest.fixture
def api_client():
    """Provide an HTTP session for individual tests."""
    with requests.Session() as session:
        yield session


@pytest.fixture
def created_objects(api):
    """Track and clean up objects created during a test."""
    objects = []

    def track(entity_type, entity_id):
        if entity_type not in ("todos", "projects", "categories"):
            raise ValueError("Unknown entity type")

        objects.append((entity_type, entity_id))

    yield track

    errors = []

    for entity_type, entity_id in reversed(objects):
        try:
            response = api.delete(f"/{entity_type}/{entity_id}")

            if response.status_code not in (200, 204, 404):
                errors.append(
                    f"{entity_type}/{entity_id}: "
                    f"HTTP {response.status_code}"
                )
        except requests.RequestException as error:
            errors.append(
                f"{entity_type}/{entity_id}: {error}"
            )

    assert not errors, f"Cleanup failed: {errors}"

@pytest.fixture
def state_manager(api):
    """Provide a fresh state manager for each test."""
    manager = StateManager(api)

    yield manager

    # Restore registered changes after each test.
    manager.restore()
