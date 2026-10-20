"""GET and HEAD on /categories/:id, including a category that does not exist."""
import pytest

from category_support import JSON, MISSING_ID, XML, assert_content_type, error_messages, send_raw, xml_root


@pytest.mark.documented
def test_get_category_by_id_returns_it_wrapped_in_a_list(api, create_category):
    category = create_category(description="fetched by id")

    response = api.get(f"/categories/{category['id']}")

    assert response.status_code == 200
    assert_content_type(response, JSON)
    assert response.json() == {"categories": [category]}


@pytest.mark.documented
def test_get_category_by_id_as_xml(api, create_category):
    category = create_category(description="fetched as xml")

    response = send_raw(api, "GET", f"/categories/{category['id']}", accept=XML)

    assert response.status_code == 200
    assert_content_type(response, XML)
    root = xml_root(response)
    assert root.tag == "categories"
    categories = root.findall("category")
    assert len(categories) == 1
    assert categories[0].findtext("id") == category["id"]
    assert categories[0].findtext("title") == category["title"]
    assert categories[0].findtext("description") == "fetched as xml"


@pytest.mark.documented
@pytest.mark.parametrize("accept", [JSON, XML])
def test_get_missing_category_returns_404_with_an_error_message(api, accept):
    response = send_raw(api, "GET", f"/categories/{MISSING_ID}", accept=accept)

    assert response.status_code == 404
    messages = error_messages(response)
    assert messages
    assert all(isinstance(message, str) and message.strip() for message in messages)


@pytest.mark.documented
def test_head_category_by_id_returns_headers_without_a_body(api, create_category):
    category = create_category()

    response = send_raw(api, "HEAD", f"/categories/{category['id']}")

    assert response.status_code == 200
    assert_content_type(response, JSON)
    assert response.text == ""


@pytest.mark.documented
def test_head_missing_category_returns_404(api):
    response = send_raw(api, "HEAD", f"/categories/{MISSING_ID}")

    assert response.status_code == 404
