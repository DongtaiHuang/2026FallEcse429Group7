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
def test_head_category_todos(
    api,
    api_client,
    api_url,
    entity_factory,
    state_manager,
    system_snapshot,
    accept,
    linked,
):
    category = entity_factory("categories")
    todo = entity_factory("todos")
    endpoint = f"/categories/{category['id']}/todos"

    if linked:
        created = api.post(
            endpoint,
            data={"id": todo["id"]},
            headers={"Accept": "application/json"},
        )
        assert created.status_code == 201, created.text

        state_manager.track_relationship(
            "categories",
            category["id"],
            "todos",
            todo["id"],
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