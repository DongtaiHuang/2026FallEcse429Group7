"""BUG 2 - ACTUAL behaviour (PASSES today): malformed bodies get a wrongly typed, Java-flavoured error.

Malformed JSON and XML both come back as 400 with Content-Type text/html, and the JSON error and the XML link
error show Java exception text. The matching failing module is test_categories_bug02_error_format_expected.py.
"""
import pytest

from category_support import JSON, XML, project_categories_path, send_raw

pytestmark = pytest.mark.bug_actual


def test_malformed_json_error_is_declared_as_html_and_shows_the_java_exception(api):
    response = send_raw(api, "POST", "/categories", body='{"title": "x"', content_type=JSON)

    assert response.status_code == 400
    assert response.headers["Content-Type"].startswith("text/html")
    assert "java.io.EOFException" in response.text


def test_malformed_xml_error_is_declared_as_html(api):
    response = send_raw(api, "POST", "/categories", body="<category><title>x</title>", content_type=XML, accept=XML)

    assert response.status_code == 400
    assert response.headers["Content-Type"].startswith("text/html")


def test_xml_link_body_is_rejected_with_a_java_parser_message(api, create_project):
    project_id = create_project()

    response = send_raw(api, "POST", project_categories_path(project_id), body="<id>1</id>", content_type=XML, accept=XML)

    assert response.status_code == 400
    assert "java.lang.IllegalStateException" in response.text
    assert api.get(project_categories_path(project_id)).json() == {"categories": []}
