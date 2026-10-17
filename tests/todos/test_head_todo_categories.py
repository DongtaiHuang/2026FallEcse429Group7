import pytest


@pytest.mark.parametrize(
    "accept",
    ["application/json", "application/xml"],
)
@pytest.mark.parametrize(
    "linked",
    [
        pytest.param(False, id="empty"),
        pytest.param(True, id="linked"),
    ],
)
def test_head_todo_categories(
    api,
    api_client,
    api_url,
    entity_factory,
    state_manager,
    system_snapshot,
    accept,
    linked,
):
    todo = entity_factory("todos")
    category = entity_factory("categories")
    endpoint = f"/todos/{todo['id']}/categories"

    if linked:
        created = api.post(
            endpoint,
            data={"id": category["id"]},
            headers={"Accept": "application/json"},
        )
        assert created.status_code == 201, created.text

        state_manager.track_relationship(
            "todos",
            todo["id"],
            "categories",
            category["id"],
        )

    before = system_snapshot()

    get_response = api.get(
        endpoint,
        headers={"Accept": accept},
    )
    assert get_response.status_code == 200, get_response.text

    head_response = api_client.head(
        f"{api_url}{endpoint}",
        headers={"Accept": accept},
        timeout=5,
    )

    assert head_response.status_code == 200
    assert head_response.content == b""

    get_type = get_response.headers.get("Content-Type", "")
    head_type = head_response.headers.get("Content-Type", "")

    assert head_type == get_type
    assert head_type.split(";")[0].strip().lower() == accept

    assert system_snapshot() == before