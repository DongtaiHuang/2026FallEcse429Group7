"""POST /categories: creation in JSON and XML, defaults, and the mandatory/non-empty title rule."""
import pytest

from category_support import JSON, XML, assert_content_type, category_ids, category_xml, error_messages, send_raw, xml_root


@pytest.mark.documented
def test_post_category_creates_it_and_returns_201(api, state, unique_title):
    response = api.post("/categories", data={"title": unique_title, "description": "created by a test"})

    assert response.status_code == 201, response.text
    assert_content_type(response, JSON)
    created = response.json()
    state.track_created("categories", created["id"])
    assert created["title"] == unique_title
    assert created["description"] == "created by a test"
    assert api.get(f"/categories/{created['id']}").json()["categories"] == [created]


@pytest.mark.documented
def test_post_category_without_description_defaults_to_empty(api, state, unique_title):
    response = api.post("/categories", data={"title": unique_title})

    assert response.status_code == 201, response.text
    created = response.json()
    state.track_created("categories", created["id"])
    assert created["description"] == ""


@pytest.mark.documented
def test_post_category_as_xml_creates_it_and_returns_xml(api, state, unique_title):
    body = category_xml(title=unique_title, description="created in xml")

    response = send_raw(api, "POST", "/categories", body=body, content_type=XML, accept=XML)

    assert response.status_code == 201, response.text
    assert_content_type(response, XML)
    root = xml_root(response)
    category_id = root.findtext("id")
    state.track_created("categories", category_id)
    assert root.tag == "category"
    assert root.findtext("title") == unique_title
    assert root.findtext("description") == "created in xml"
    assert api.get(f"/categories/{category_id}").json()["categories"][0]["title"] == unique_title


@pytest.mark.documented
def test_post_category_creates_a_new_id_every_time(api, state, unique_title):
    first = api.post("/categories", data={"title": f"{unique_title}-first"}).json()
    second = api.post("/categories", data={"title": f"{unique_title}-second"}).json()
    state.track_created("categories", first["id"])
    state.track_created("categories", second["id"])

    assert first["id"] != second["id"]


REJECTED_BODIES = {
    "empty object": ({}, "mandatory"),
    "description only": ({"description": "no title"}, "mandatory"),
    "empty title": ({"title": ""}, "can not be empty"),
}


@pytest.mark.documented
@pytest.mark.parametrize("body, reason", REJECTED_BODIES.values(), ids=REJECTED_BODIES.keys())
def test_post_category_without_a_valid_title_returns_400_and_creates_nothing(api, body, reason):
    before = category_ids(api)

    response = api.post("/categories", data=body)

    assert response.status_code == 400
    assert any(reason in message for message in error_messages(response))
    assert category_ids(api) == before


@pytest.mark.documented
def test_post_category_with_an_empty_title_in_xml_returns_400_and_creates_nothing(api):
    before = category_ids(api)

    response = send_raw(api, "POST", "/categories", body=category_xml(title=""), content_type=XML, accept=XML)

    assert response.status_code == 400
    assert category_ids(api) == before
