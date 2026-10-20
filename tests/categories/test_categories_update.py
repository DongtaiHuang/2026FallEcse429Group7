"""POST and PUT on /categories/:id: partial update, full update, rejected updates and missing ids.

Observed in exploration: POST keeps the fields left out of the body, PUT resets them. The /docs page describes
both as "amend", so these two tests record the behaviour the app has today.
"""
import pytest

from category_support import MISSING_ID, XML, category_ids, category_xml, error_messages, send_raw


@pytest.mark.documented
def test_post_on_an_id_updates_only_the_fields_in_the_body(api, create_category, unique_title):
    category = create_category(description="kept")

    response = api.post(f"/categories/{category['id']}", data={"title": unique_title})

    assert response.status_code == 200, response.text
    assert response.json() == {"id": category["id"], "title": unique_title, "description": "kept"}
    assert api.get(f"/categories/{category['id']}").json()["categories"] == [response.json()]


@pytest.mark.documented
def test_put_on_an_id_replaces_the_category_and_resets_left_out_fields(api, create_category, unique_title):
    category = create_category(description="will be reset")

    response = api.put(f"/categories/{category['id']}", data={"title": unique_title})

    assert response.status_code == 200, response.text
    assert response.json() == {"id": category["id"], "title": unique_title, "description": ""}
    assert api.get(f"/categories/{category['id']}").json()["categories"] == [response.json()]


@pytest.mark.documented
def test_put_with_every_field_replaces_both(api, create_category, unique_title):
    category = create_category(description="old")

    response = api.put(f"/categories/{category['id']}", data={"title": unique_title, "description": "new"})

    assert response.status_code == 200, response.text
    assert response.json() == {"id": category["id"], "title": unique_title, "description": "new"}


@pytest.mark.documented
def test_post_on_an_id_as_xml_updates_the_title(api, create_category, unique_title):
    category = create_category(description="kept in xml update")

    response = send_raw(
        api, "POST", f"/categories/{category['id']}", body=category_xml(title=unique_title), content_type=XML, accept=XML
    )

    assert response.status_code == 200, response.text
    assert api.get(f"/categories/{category['id']}").json()["categories"][0]["title"] == unique_title


@pytest.mark.documented
@pytest.mark.parametrize("method", ["post", "put"])
def test_update_with_an_empty_title_returns_400_and_changes_nothing(api, create_category, method):
    category = create_category(description="unchanged")

    response = getattr(api, method)(f"/categories/{category['id']}", data={"title": ""})

    assert response.status_code == 400
    assert any("can not be empty" in message for message in error_messages(response))
    assert api.get(f"/categories/{category['id']}").json()["categories"] == [category]


@pytest.mark.documented
@pytest.mark.parametrize("method", ["post", "put"])
def test_update_of_a_missing_category_returns_404_and_creates_nothing(api, method):
    before = category_ids(api)

    response = getattr(api, method)(f"/categories/{MISSING_ID}", data={"title": "ghost"})

    assert response.status_code == 404
    assert error_messages(response)
    assert category_ids(api) == before
