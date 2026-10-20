"""Helpers shared by the category test modules (/categories and the project-category link paths)."""
import json
import xml.etree.ElementTree as ElementTree

JSON = "application/json"
XML = "application/xml"
MISSING_ID = "999999"
HTTP_TIMEOUT_SECONDS = 5
ENTITY_COLLECTIONS = ("todos", "projects", "categories")


def project_categories_path(project_id):
    return f"/projects/{project_id}/categories"


def category_projects_path(category_id):
    return f"/categories/{category_id}/projects"


def category_xml(title=None, description=None, with_id=False):
    """XML body for a category.

    The id element is left out by default: the /docs example shows <id>null</id> on input, but the app rejects it
    with 400 "Not allowed to create with id" (see the bug 3 modules).
    """
    parts = []
    if description is not None:
        parts.append(f"<description>{description}</description>")
    if with_id:
        parts.append("<id>null</id>")
    if title is not None:
        parts.append(f"<title>{title}</title>")
    return "<category>" + "".join(parts) + "</category>"


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


def xml_ids(response, child_tag):
    """Ids of the `child_tag` elements in an XML list response."""
    return [element.findtext("id") for element in xml_root(response).findall(child_tag)]


def error_messages(response):
    """The error messages of a JSON or XML error response."""
    if response.headers.get("Content-Type", "").startswith(XML):
        return [element.text for element in xml_root(response).findall("errorMessage")]
    return response.json()["errorMessages"]


def assert_content_type(response, expected):
    actual = response.headers.get("Content-Type", "")
    assert actual.startswith(expected), f"Content-Type is {actual!r}, expected {expected!r}"


def allowed_methods(response):
    header = response.headers.get("Allow", "")
    return {method.strip() for method in header.split(",") if method.strip()}


def category_ids(api):
    return ids_in(api.get("/categories"), "categories")


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
