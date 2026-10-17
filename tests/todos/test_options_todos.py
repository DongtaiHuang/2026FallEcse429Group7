import pytest


@pytest.mark.parametrize(
    "accept",
    ["application/json", "application/xml"],
)
@pytest.mark.parametrize(
    "path, expected_allow",
    [
        pytest.param(
            "/todos",
            "OPTIONS, GET, HEAD, POST",
            id="todos",
        ),
        pytest.param(
            "/todos/{todo_id}",
            "OPTIONS, GET, HEAD, POST, PUT, DELETE",
            id="todo-by-id",
        ),
        pytest.param(
            "/todos/{todo_id}/categories",
            "OPTIONS, GET, HEAD, POST",
            id="todo-categories",
        ),
        pytest.param(
            "/categories/{category_id}/todos",
            "OPTIONS, GET, HEAD, POST",
            id="category-todos",
        ),
        pytest.param(
            "/todos/{todo_id}/categories/{category_id}",
            "OPTIONS, DELETE",
            id="todo-category-link",
        ),
        pytest.param(
            "/categories/{category_id}/todos/{todo_id}",
            "OPTIONS, DELETE",
            id="category-todo-link",
        ),
    ],
)
def test_options_returns_allowed_methods(
    api_client,
    api_url,
    entity_factory,
    system_snapshot,
    accept,
    path,
    expected_allow,
):
    todo = entity_factory("todos")
    category = entity_factory("categories")

    endpoint = path.format(
        todo_id=todo["id"],
        category_id=category["id"],
    )

    before = system_snapshot()

    response = api_client.options(
        f"{api_url}{endpoint}",
        headers={"Accept": accept},
        timeout=5,
    )

    assert response.status_code == 200, response.text
    assert response.content == b""

    actual_methods = {
        method.strip()
        for method in response.headers.get("Allow", "").split(",")
        if method.strip()
    }
    expected_methods = {
        method.strip()
        for method in expected_allow.split(",")
    }

    assert actual_methods == expected_methods
    assert system_snapshot() == before