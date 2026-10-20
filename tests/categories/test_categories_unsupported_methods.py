"""Invalid operations: HTTP methods the category paths do not support.

The 405 status follows the swagger file; it was not checked in the exploratory sessions, so a failure here
may mean the app answers differently (for example 404) and the assertion should be adjusted and logged.
"""
import pytest

from category_support import category_ids, send_raw


@pytest.mark.documented
@pytest.mark.parametrize("method", ["PUT", "PATCH", "DELETE"])
def test_categories_collection_rejects_method_with_405(api, create_category, method):
    category = create_category()
    before = category_ids(api)

    response = send_raw(api, method, "/categories", body='{"title": "x"}')

    assert response.status_code == 405
    assert category_ids(api) == before
    assert api.get(f"/categories/{category['id']}").status_code == 200


@pytest.mark.documented
def test_category_item_rejects_patch_with_405(api, create_category):
    category = create_category(description="unchanged")

    response = send_raw(api, "PATCH", f"/categories/{category['id']}", body='{"title": "x"}')

    assert response.status_code == 405
    assert api.get(f"/categories/{category['id']}").json()["categories"] == [category]
