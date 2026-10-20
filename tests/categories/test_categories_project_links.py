"""The project-category links: /projects/:id/categories and /categories/:id/projects.

Observed in exploration: the two directions are independent relationships, so a link made from one side is not
visible from the other. The independence tests record that behaviour; the docs do not describe it either way.
"""
import pytest

from category_support import MISSING_ID, category_projects_path, error_messages, ids_in, project_categories_path


@pytest.mark.documented
def test_post_project_categories_links_the_category(api, state, create_project, create_category):
    project_id, category = create_project(), create_category()

    response = api.post(project_categories_path(project_id), data={"id": category["id"]})
    state.track_relationship("projects", project_id, "categories", category["id"])

    assert response.status_code == 201
    assert response.text == ""
    assert ids_in(api.get(project_categories_path(project_id)), "categories") == [category["id"]]


@pytest.mark.documented
def test_get_project_categories_is_empty_for_a_project_without_links(api, create_project):
    response = api.get(project_categories_path(create_project()))

    assert response.status_code == 200
    assert response.json() == {"categories": []}


@pytest.mark.documented
def test_get_project_categories_returns_the_full_category(api, create_project, create_category, link_category_to_project):
    project_id, category = create_project(), create_category(description="linked")
    link_category_to_project(project_id, category["id"])

    response = api.get(project_categories_path(project_id))

    assert response.status_code == 200
    assert response.json() == {"categories": [category]}


@pytest.mark.documented
def test_link_from_the_category_side_is_listed_on_the_category(api, create_project, create_category, link_project_to_category):
    project_id, category = create_project(), create_category()
    link_project_to_category(category["id"], project_id)

    response = api.get(category_projects_path(category["id"]))

    assert response.status_code == 200
    assert ids_in(response, "projects") == [project_id]


@pytest.mark.undocumented
def test_project_side_link_is_not_visible_from_the_category_side(api, create_project, create_category, link_category_to_project):
    project_id, category = create_project(), create_category()
    link_category_to_project(project_id, category["id"])

    assert api.get(category_projects_path(category["id"])).json() == {"projects": []}


@pytest.mark.undocumented
def test_category_side_link_is_not_visible_from_the_project_side(api, create_project, create_category, link_project_to_category):
    project_id, category = create_project(), create_category()
    link_project_to_category(category["id"], project_id)

    assert api.get(project_categories_path(project_id)).json() == {"categories": []}


@pytest.mark.documented
def test_delete_link_removes_only_the_link(api, create_project, create_category, link_category_to_project):
    project_id, category = create_project(), create_category(description="stays")
    link_category_to_project(project_id, category["id"])

    response = api.delete(f"{project_categories_path(project_id)}/{category['id']}")

    assert response.status_code == 200
    assert api.get(project_categories_path(project_id)).json() == {"categories": []}
    assert api.get(f"/categories/{category['id']}").json()["categories"] == [category]


@pytest.mark.documented
def test_delete_link_twice_returns_404_the_second_time(api, create_project, create_category, link_category_to_project):
    project_id, category = create_project(), create_category()
    link_category_to_project(project_id, category["id"])
    link_path = f"{project_categories_path(project_id)}/{category['id']}"
    assert api.delete(link_path).status_code == 200

    second = api.delete(link_path)

    assert second.status_code == 404
    assert error_messages(second)


@pytest.mark.documented
def test_delete_link_that_never_existed_returns_404(api, create_project, create_category):
    project_id, category = create_project(), create_category()

    response = api.delete(f"{project_categories_path(project_id)}/{category['id']}")

    assert response.status_code == 404
    assert error_messages(response)


@pytest.mark.undocumented
def test_duplicate_link_returns_201_but_creates_one_link(api, create_project, create_category, link_category_to_project):
    project_id, category = create_project(), create_category()
    link_category_to_project(project_id, category["id"])

    duplicate = api.post(project_categories_path(project_id), data={"id": category["id"]})

    assert duplicate.status_code == 201
    assert ids_in(api.get(project_categories_path(project_id)), "categories") == [category["id"]]


@pytest.mark.documented
def test_link_to_a_missing_category_returns_404_and_links_nothing(api, create_project):
    project_id = create_project()

    response = api.post(project_categories_path(project_id), data={"id": MISSING_ID})

    assert response.status_code == 404
    assert error_messages(response)
    assert api.get(project_categories_path(project_id)).json() == {"categories": []}


@pytest.mark.documented
def test_one_project_can_link_to_several_categories(api, create_project, create_category, link_category_to_project):
    project_id = create_project()
    first, second = create_category(), create_category()
    link_category_to_project(project_id, first["id"])
    link_category_to_project(project_id, second["id"])

    assert sorted(ids_in(api.get(project_categories_path(project_id)), "categories")) == sorted([first["id"], second["id"]])
