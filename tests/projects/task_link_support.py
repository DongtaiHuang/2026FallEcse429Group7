"""Helpers shared by the project-todo link test modules (/projects/:id/tasks, /todos/:id/tasksof)."""
import json
import xml.etree.ElementTree as ElementTree

JSON = "application/json"
XML = "application/xml"
MISSING_ID = "999999"
HTTP_TIMEOUT_SECONDS = 5
ENTITY_COLLECTIONS = ("todos", "projects", "categories")


def project_tasks_path(project_id):
    return f"/projects/{project_id}/tasks"


def todo_projects_path(todo_id):
    return f"/todos/{todo_id}/tasksof"


def send_raw(api, method, path, body=None, content_type=JSON, accept=JSON):
    """Send a request whose body and headers APIHelper cannot express (XML, malformed JSON, HEAD...)."""
    headers = {"Accept": accept}
    if body is not None:
        headers["Content-Type"] = content_type
    return api.session.request(
        method,
        f"{api.base_url}{path}",
        data=body,
        headers=headers,
        timeout=HTTP_TIMEOUT_SECONDS,
    )


def ids_in(response, key):
    """Ids listed under `key` in a JSON response, in response order."""
    return [item["id"] for item in response.json().get(key, [])]


def xml_root(response):
    return ElementTree.fromstring(response.text)


def assert_content_type(response, expected):
    actual = response.headers.get("Content-Type", "")
    assert actual.startswith(expected), f"Content-Type is {actual!r}, expected {expected!r}"


def allowed_methods(response):
    header = response.headers.get("Allow", "")
    return {method.strip() for method in header.split(",") if method.strip()}


def snapshot(api):
    """Order-insensitive copy of every todo, project and category, used to prove state was restored."""
    return {
        collection: _normalise(api.get(f"/{collection}").json()[collection])
        for collection in ENTITY_COLLECTIONS
    }


def _normalise(value):
    if isinstance(value, dict):
        return {key: _normalise(item) for key, item in value.items()}
    if isinstance(value, list):
        items = [_normalise(item) for item in value]
        return sorted(items, key=lambda item: json.dumps(item, sort_keys=True))
    return value
