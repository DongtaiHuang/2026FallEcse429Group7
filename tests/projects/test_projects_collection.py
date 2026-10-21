"""API under test: /projects collection endpoints (documented) - GET, HEAD, OPTIONS, POST."""
import pytest

pytestmark = pytest.mark.documented


def test_get_projects_returns_200_and_list(api):
    """GET /projects returns 200 OK and lists existing projects including default startup data[cite: 1]."""
    response = api.get("/projects")
    assert response.status_code == 200
    data = response.json()
    assert "projects" in data
    assert isinstance(data["projects"], list)
    project_ids = [p["id"] for p in data["projects"]]
    assert "1" in project_ids  # Default startup project "Office Work"[cite: 1]


def test_head_projects_returns_200_with_empty_body(api, api_client):
    """HEAD /projects returns 200 OK with an empty body and expected headers[cite: 1]."""
    response = api_client.head(f"{api.base_url}/projects")
    assert response.status_code == 200
    assert response.text == ""
    assert response.headers.get("Content-Type") == "application/json"


def test_options_projects_returns_200_and_allowed_methods(api, api_client):
    """OPTIONS /projects returns 200 OK with Allow header matching documented methods[cite: 1, 2]."""
    response = api_client.options(f"{api.base_url}/projects")
    assert response.status_code == 200
    assert response.text == ""
    allow_header = response.headers.get("Allow", "")
    for method in ["OPTIONS", "GET", "HEAD", "POST"]:
        assert method in allow_header


def test_post_projects_creates_new_project_returning_201(api, state):
    """POST /projects successfully creates a new project with 201 Created[cite: 2]."""
    payload = {
        "title": "Test project",
        "completed": False,
        "active": True,
        "description": "My first project"
    }
    response = api.post("/projects", data=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test project"
    assert data["active"] == "true"  # Booleans are stored/returned as strings[cite: 1, 2]
    state.track_created("projects", data["id"])


def test_post_projects_invalid_boolean_type_returns_400(api):
    """POST /projects with invalid boolean field type rejects with 400 Bad Request[cite: 2]."""
    payload = {"title": "x", "completed": "not-a-boolean"}
    response = api.post("/projects", data=payload)
    assert response.status_code == 400
    assert "errorMessages" in response.json()