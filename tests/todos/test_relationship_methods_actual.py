import pytest


@pytest.mark.parametrize(
    "accept",
    ["application/json", "application/xml"],
)
@pytest.mark.parametrize(
    "method, parent_type",
    [
        pytest.param("GET", "todos", id="get-todo-category"),
        pytest.param("HEAD", "categories", id="head-category-todo"),
    ],
)
def test_relationship_method_currently_returns_404(
    api_client,
    api_url,
    relationship_method_paths,
    system_snapshot,
    accept,
    method,
    parent_type,
):
    endpoint = relationship_method_paths[parent_type]
    before = system_snapshot()

    response = api_client.request(
        method,
        f"{api_url}{endpoint}",
        headers={"Accept": accept},
        timeout=5,
        allow_redirects=False,
    )

    assert system_snapshot() == before
    assert response.status_code == 404, response.text
    assert response.content == b""