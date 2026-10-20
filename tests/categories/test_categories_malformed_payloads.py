"""Invalid input: malformed JSON and XML bodies sent to POST /categories.

Asserts what the app does today (400 and nothing created). The wrong Content-Type and the leaked Java text of
these error responses are covered by the bug 2 modules.
"""
import pytest

from category_support import JSON, XML, category_ids, send_raw

MALFORMED_JSON_BODIES = {
    "closing brace missing": '{"title": "x"',
    "not json at all": "not json at all",
    "json array instead of object": '[{"title": "x"}]',
}


@pytest.mark.documented
@pytest.mark.parametrize("body", MALFORMED_JSON_BODIES.values(), ids=MALFORMED_JSON_BODIES.keys())
def test_malformed_json_returns_400_and_creates_nothing(api, body):
    before = category_ids(api)

    response = send_raw(api, "POST", "/categories", body=body, content_type=JSON)

    assert response.status_code == 400
    assert "errorMessages" in response.text
    assert category_ids(api) == before


@pytest.mark.documented
def test_malformed_xml_returns_400_and_creates_nothing(api):
    before = category_ids(api)

    response = send_raw(api, "POST", "/categories", body="<category><title>broken</title>", content_type=XML, accept=XML)

    assert response.status_code == 400
    assert "errorMessage" in response.text
    assert category_ids(api) == before


@pytest.mark.documented
def test_malformed_json_on_an_update_returns_400_and_changes_nothing(api, create_category):
    category = create_category(description="unchanged")

    response = send_raw(api, "PUT", f"/categories/{category['id']}", body='{"title": "x"', content_type=JSON)

    assert response.status_code == 400
    assert api.get(f"/categories/{category['id']}").json()["categories"] == [category]


@pytest.mark.documented
def test_missing_body_returns_400_and_creates_nothing(api):
    before = category_ids(api)

    response = send_raw(api, "POST", "/categories", body="", content_type=JSON)

    assert response.status_code == 400
    assert category_ids(api) == before
