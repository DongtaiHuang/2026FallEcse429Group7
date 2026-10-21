"""API under test: /projects/:id item endpoints (documented) - GET, POST, PUT, DELETE."""
import pytest

pytestmark = pytest.mark.documented


def test_get_project_by_id_returns_200_wrapped_in_array(api, create_project):
    """GET /projects/:id returns 200 OK with the project wrapped in a 'projects' array[cite: 2]."""
    project_id = create_project(title="Fetch Test")
    response = api.get(f"/projects/{project_id}")
    assert response.status_code == 200
    data = response.json()
    assert "projects" in data
    assert isinstance(data["projects"], list)
    assert data["projects"][0]["id"] == project_id
    assert data["projects"][0]["title"] == "Fetch Test"


def test_get_nonexistent_project_returns_404(api):
    """GET /projects/:id for a nonexistent ID returns 404 Not Found[cite: 2]."""
    response = api.get("/projects/9999")
    assert response.status_code == 404
    assert "errorMessages" in response.json()


def test_post_project_partial_update_preserves_omitted_fields(api, create_project):
    """POST /projects/:id performs a partial update, amending title while preserving omitted fields[cite: 2]."""
    project_id = create_project(title="Original Title", description="Keep Me", active=True)
    response = api.post(f"/projects/{project_id}", data={"title": "Updated via POST"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated via POST"
    assert data["description"] == "Keep Me"  # Omitted fields preserved[cite: 2]
    assert data["active"] == "true"


def test_put_project_full_update_resets_omitted_fields(api, create_project):
    """PUT /projects/:id performs a full update, resetting omitted fields to defaults[cite: 2]."""
    project_id = create_project(title="Original Title", description="Clear Me", active=True)
    response = api.put(f"/projects/{project_id}", data={"title": "Updated via PUT"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated via PUT"
    assert data["description"] == ""  # Omitted fields reset[cite: 2]
    assert data["active"] == "false"


def test_delete_project_returns_200_and_removes_it(api, create_project):
    """DELETE /projects/:id successfully removes the project and subsequent GET returns 404[cite: 3]."""
    project_id = create_project(title="Delete Me")
    response = api.delete(f"/projects/{project_id}")
    assert response.status_code == 200
    assert response.text == ""

    get_response = api.get(f"/projects/{project_id}")
    assert get_response.status_code == 404