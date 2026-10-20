"""Precondition for every module: the Todo Manager must be reachable and serving JSON."""
import pytest
import requests


@pytest.fixture(scope="session", autouse=True)
def check_service_running():
    """Overrides the root conftest's session check so this test reports FAILED, not ERROR, when the app is down."""


@pytest.fixture(autouse=True)
def service_must_be_running():
    """Overrides the folder-wide fixture so this test reports FAILED, not ERROR, when the app is down."""


@pytest.fixture(autouse=True)
def system_state_is_restored():
    """Overrides the folder-wide fixture: this test only reads."""


def test_todo_manager_service_is_running(api):
    try:
        response = api.get("/todos")
    except requests.RequestException as error:
        raise AssertionError(f"Todo Manager is not running at {api.base_url}: {error}") from error

    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("application/json")
