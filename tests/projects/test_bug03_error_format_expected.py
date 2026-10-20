"""BUG 3 - EXPECTED behaviour (FAILS today): error responses for bad link requests.

Errors should declare the format of their body (JSON or XML) and must not expose Java exception text.
The matching passing module is test_bug03_error_format_actual.py.
"""
import pytest

from task_link_support import JSON, XML, assert_content_type, project_tasks_path, send_raw

pytestmark = pytest.mark.bug_expected


def post_malformed_json(api, project_id):
    return send_raw(api, "POST", project_tasks_path(project_id), body='{"id": "1"', content_type=JSON)


def test_malformed_json_error_is_declared_as_json(api, create_project):
    response = post_malformed_json(api, create_project())

    assert_content_type(response, JSON)


def test_malformed_json_error_does_not_expose_java_internals(api, create_project):
    response = post_malformed_json(api, create_project())

    assert "java." not in response.text


def test_malformed_xml_error_is_declared_as_xml(api, create_project):
    response = send_raw(api, "POST", project_tasks_path(create_project()), body="<todo><id>1</id>", content_type=XML, accept=XML)

    assert_content_type(response, XML)


def test_unknown_field_in_link_body_does_not_expose_java_internals(api, create_project, create_todo):
    project_id, todo_id = create_project(), create_todo()

    response = api.post(project_tasks_path(project_id), data={"id": todo_id, "bogus": 1})

    assert "Cannot invoke" not in response.text


def test_unknown_field_error_is_declared_as_json(api, create_project, create_todo):
    project_id, todo_id = create_project(), create_todo()

    response = api.post(project_tasks_path(project_id), data={"id": todo_id, "bogus": 1})

    assert_content_type(response, JSON)
