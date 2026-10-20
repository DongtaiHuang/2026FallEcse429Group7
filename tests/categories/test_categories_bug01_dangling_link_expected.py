"""BUG 1 - EXPECTED behaviour (FAILS today): deleting a category must remove its links to projects.

After DELETE /categories/:id, GET /projects/:id/categories must no longer list the deleted category.
The matching passing module is test_categories_bug01_dangling_link_actual.py.
"""
import pytest

from category_support import ids_in, project_categories_path

pytestmark = pytest.mark.bug_expected


def test_deleted_category_is_not_listed_under_its_project(api, create_project, create_category, link_category_to_project):
    project_id, category = create_project(), create_category()
    link_category_to_project(project_id, category["id"])
    assert api.delete(f"/categories/{category['id']}").status_code == 200

    listed = ids_in(api.get(project_categories_path(project_id)), "categories")

    assert category["id"] not in listed


def test_deleted_category_cannot_be_unlinked_afterwards(api, create_project, create_category, link_category_to_project):
    project_id, category = create_project(), create_category()
    link_category_to_project(project_id, category["id"])
    api.delete(f"/categories/{category['id']}")

    response = api.delete(f"{project_categories_path(project_id)}/{category['id']}")

    assert response.status_code == 404
