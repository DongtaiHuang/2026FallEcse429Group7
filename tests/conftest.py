
import os

import pytest
import requests

BASE_URL = os.getenv("TODO_API_URL", "http://localhost:4567")


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
