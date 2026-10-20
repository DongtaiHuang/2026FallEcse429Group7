"""GET, HEAD and OPTIONS on /categories, including the documented query-parameter filters."""
import pytest

from category_support import JSON, XML, allowed_methods, assert_content_type, send_raw, xml_ids, xml_root


@pytest.mark.documented
def test_get_categories_lists_a_created_category(api, create_category):
    category = create_category(description="listed")

    response = api.get("/categories")

    assert response.status_code == 200
    assert_content_type(response, JSON)
    assert category in response.json()["categories"]


@pytest.mark.documented
def test_get_categories_as_xml_lists_a_created_category(api, create_category):
    category = create_category(description="listed in xml")

    response = send_raw(api, "GET", "/categories", accept=XML)

    assert response.status_code == 200
    assert_content_type(response, XML)
    assert xml_root(response).tag == "categories"
    assert category["id"] in xml_ids(response, "category")


@pytest.mark.documented
def test_get_categories_changes_nothing(api, create_category):
    create_category()
    before = api.get("/categories").json()

    api.get("/categories")

    assert api.get("/categories").json() == before


@pytest.mark.documented
def test_head_categories_returns_headers_without_a_body(api):
    response = send_raw(api, "HEAD", "/categories")

    assert response.status_code == 200
    assert_content_type(response, JSON)
    assert response.text == ""


@pytest.mark.documented
def test_options_categories_lists_the_documented_methods(api):
    response = send_raw(api, "OPTIONS", "/categories")

    assert response.status_code == 200
    assert {"GET", "HEAD", "POST"} <= allowed_methods(response)


@pytest.mark.documented
def test_filter_by_title_returns_only_matching_categories(api, create_category, unique_title):
    wanted = create_category(title=unique_title, description="filter target")
    create_category()

    response = api.get("/categories", params={"title": unique_title})

    assert response.status_code == 200
    assert response.json()["categories"] == [wanted]


@pytest.mark.documented
def test_filter_matching_nothing_returns_an_empty_list(api, unique_title):
    response = api.get("/categories", params={"title": unique_title})

    assert response.status_code == 200
    assert response.json() == {"categories": []}
