import pytest


@pytest.mark.parametrize(
    "accept",
    ["application/json", "application/xml"],
)
@pytest.mark.parametrize(
    "method, path",
    [
        pytest.param(
            "PUT",
            "/todos",
            id="put-todos",
        ),
        pytest.param(
            "PATCH",
            "/todos/{todo_id}",
            id="patch-todo",
        ),
        pytest.param(
            "DELETE",
            "/todos/{todo_id}/categories",
            id="delete-category-collection",
        ),
        pytest.param(
            "PUT",
            "/categories/{category_id}/todos",
            id="put-todo-collection",
        ),
    ],
)
def test_unsupported_todo_method(
    api_client,
    api_url,
    entity_factory,
    system_snapshot,
    accept,
    method,
    path,
):
    todo = entity_factory("todos")
    category = entity_factory("categories")

    endpoint = path.format(
        todo_id=todo["id"],
        category_id=category["id"],
    )

    before = system_snapshot()

    response = api_client.request(
        method,
        f"{api_url}{endpoint}",
        json={"title": "Unsupported method probe"},
        headers={"Accept": accept},
        timeout=5,
    )

    assert response.status_code == 405, response.text
    assert response.content == b""
    assert system_snapshot() == before