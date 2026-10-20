"""BUG 3 - EXPECTED behaviour (FAILS today): the XML input example from /docs must create a category.

The /docs page shows <id>null</id> in its XML input example for category. The matching passing module is
test_categories_bug03_documented_xml_example_actual.py.
"""
import pytest

from category_support import XML, category_xml, send_raw, xml_root

pytestmark = pytest.mark.bug_expected


def test_documented_xml_example_with_a_null_id_creates_the_category(api, state, unique_title):
    body = category_xml(title=unique_title, description="docs example", with_id=True)

    response = send_raw(api, "POST", "/categories", body=body, content_type=XML, accept=XML)
    if response.status_code == 201:
        state.track_created("categories", xml_root(response).findtext("id"))

    assert response.status_code == 201, response.text
