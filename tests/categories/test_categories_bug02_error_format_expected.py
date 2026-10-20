"""BUG 2 - EXPECTED behaviour (FAILS today): error responses for malformed category requests.

Errors should declare the format of their body (JSON or XML) and must not expose Java exception text.
The matching passing module is test_categories_bug02_error_format_actual.py.
"""
import pytest

from category_support import JSON, XML, assert_content_type, project_categories_path, send_raw

pytestmark = pytest.mark.bug_expected


def post_malformed_json(api):
    return send_raw(api, "POST", "/categories", body='{"title": "x"', content_type=JSON)


def test_malformed_json_error_is_declared_as_json(api):
    assert_content_type(post_malformed_json(api), JSON)


def test_malformed_json_error_does_not_expose_java_internals(api):
    assert "java." not in post_malformed_json(api).text


def test_malformed_xml_error_is_declared_as_xml(api):
    response = send_raw(api, "POST", "/categories", body="<category><title>x</title>", content_type=XML, accept=XML)

    assert_content_type(response, XML)


def test_xml_link_body_does_not_expose_java_internals(api, create_project):
    response = send_raw(
        api, "POST", project_categories_path(create_project()), body="<id>1</id>", content_type=XML, accept=XML
    )

    assert "java." not in response.text
