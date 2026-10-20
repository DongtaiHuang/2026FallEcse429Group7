"""DELETE /categories/:id: deletion, repeated deletion and a category that never existed."""
import pytest

from category_support import MISSING_ID, category_ids, error_messages


@pytest.mark.documented
def test_delete_category_returns_200_and_removes_it(api, create_category):
    category = create_category()

    response = api.delete(f"/categories/{category['id']}")

    assert response.status_code == 200
    assert response.text == ""
    assert api.get(f"/categories/{category['id']}").status_code == 404
    assert category["id"] not in category_ids(api)


@pytest.mark.documented
def test_delete_category_leaves_other_categories_alone(api, create_category):
    doomed, survivor = create_category(), create_category(description="survives")

    api.delete(f"/categories/{doomed['id']}")

    assert api.get(f"/categories/{survivor['id']}").json()["categories"] == [survivor]


@pytest.mark.documented
def test_delete_category_twice_returns_404_the_second_time(api, create_category):
    category = create_category()
    assert api.delete(f"/categories/{category['id']}").status_code == 200

    second = api.delete(f"/categories/{category['id']}")

    assert second.status_code == 404
    assert error_messages(second)


@pytest.mark.documented
def test_delete_missing_category_returns_404_and_changes_nothing(api):
    before = category_ids(api)

    response = api.delete(f"/categories/{MISSING_ID}")

    assert response.status_code == 404
    assert error_messages(response)
    assert category_ids(api) == before
