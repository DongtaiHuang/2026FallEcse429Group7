"""BUG 1 - ACTUAL behaviour (PASSES today): a deleted category stays linked to its project.

The category itself is gone (404), but GET /projects/:id/categories still lists it and the dangling link can
still be removed. The matching failing module is test_categories_bug01_dangling_link_expected.py.
"""
import pytest

from category_support import ids_in, project_categories_path

pytestmark = pytest.mark.bug_actual


def test_deleted_category_is_still_listed_under_its_project(api, create_project, create_category, link_category_to_project):
    project_id, category = create_project(), create_category()
    link_category_to_project(project_id, category["id"])

    assert api.delete(f"/categories/{category['id']}").status_code == 200

    assert api.get(f"/categories/{category['id']}").status_code == 404
    assert ids_in(api.get(project_categories_path(project_id)), "categories") == [category["id"]]


def test_dangling_link_to_a_deleted_category_can_still_be_unlinked(api, create_project, create_category, link_category_to_project):
    project_id, category = create_project(), create_category()
    link_category_to_project(project_id, category["id"])
    api.delete(f"/categories/{category['id']}")

    response = api.delete(f"{project_categories_path(project_id)}/{category['id']}")

    assert response.status_code == 200
    assert api.get(project_categories_path(project_id)).json() == {"categories": []}
