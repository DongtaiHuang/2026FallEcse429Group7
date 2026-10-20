"""BUG 3 - ACTUAL behaviour (PASSES today): the XML input example from /docs is rejected.

The example contains <id>null</id>; the app answers 400 "Not allowed to create with id" and creates nothing.
The same body without the id element is accepted. The matching failing module is
test_categories_bug03_documented_xml_example_expected.py.
"""
import pytest

from category_support import XML, category_ids, category_xml, send_raw, xml_root

pytestmark = pytest.mark.bug_actual


def test_documented_xml_example_with_a_null_id_is_rejected(api, unique_title):
    before = category_ids(api)
    body = category_xml(title=unique_title, description="docs example", with_id=True)

    response = send_raw(api, "POST", "/categories", body=body, content_type=XML, accept=XML)

    assert response.status_code == 400
    assert "Not allowed to create with id" in response.text
    assert category_ids(api) == before


def test_documented_xml_example_is_accepted_once_the_id_element_is_removed(api, state, unique_title):
    body = category_xml(title=unique_title, description="docs example without id")

    response = send_raw(api, "POST", "/categories", body=body, content_type=XML, accept=XML)
    if response.status_code == 201:
        state.track_created("categories", xml_root(response).findtext("id"))

    assert response.status_code == 201, response.text
