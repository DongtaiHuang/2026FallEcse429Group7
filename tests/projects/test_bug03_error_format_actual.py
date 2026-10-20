"""BUG 3 - ACTUAL behaviour (PASSES today): error responses for bad link requests.

Errors are sent as text/html even though their bodies are JSON or XML, and some expose Java exception
text. Expected behaviour is in test_bug03_error_format_expected.py.
"""
import pytest

from task_link_support import JSON, XML, ids_in, project_tasks_path, send_raw, xml_root

pytestmark = pytest.mark.bug_actual

HTML = "text/html"


def test_malformed_json_error_is_sent_as_html_with_a_java_exception(api, create_project):
    response = send_raw(api, "POST", project_tasks_path(create_project()), body='{"id": "1"', content_type=JSON)

    assert response.status_code == 400
    assert response.headers["Content-Type"].startswith(HTML)
    assert "java.io.EOFException" in response.json()["errorMessages"][0]


def test_malformed_xml_error_is_sent_as_html_although_the_body_is_xml(api, create_project):
    response = send_raw(api, "POST", project_tasks_path(create_project()), body="<todo><id>1</id>", content_type=XML, accept=XML)

    assert response.status_code == 400
    assert response.headers["Content-Type"].startswith(HTML)
    assert xml_root(response).tag == "errorMessages"


def test_unknown_field_in_link_body_returns_400_with_a_java_message(api, create_project, create_todo):
    project_id, todo_id = create_project(), create_todo()

    response = api.post(project_tasks_path(project_id), data={"id": todo_id, "bogus": 1})

    assert response.status_code == 400
    assert response.headers["Content-Type"].startswith(HTML)
    assert "Cannot invoke" in response.text
    assert ids_in(api.get(project_tasks_path(project_id)), "todos") == []


def test_control_not_found_errors_are_correctly_sent_as_json(api, create_project):
    response = api.post(project_tasks_path(create_project()), data={"id": "999999"})

    assert response.status_code == 404
    assert response.headers["Content-Type"].startswith(JSON)
