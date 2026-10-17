from uuid import uuid4

import pytest


@pytest.mark.parametrize(
    "accept",
    ["application/json", "application/xml"],
)
@pytest.mark.parametrize(
    "todo_exists",
    [
        pytest.param(True, id="existing"),
        pytest.param(False, id="missing"),
    ],
)
def test_head_todo_by_id(
    api,
    api_client,
    api_url,
    state_manager,
    system_snapshot,
    accept,
    todo_exists,
):
    # Create a temporary Todo owned by this test.
    created = api.post(
        "/todos",
        data={"title": f"pytest-head-{uuid4().hex}"},
        headers={"Accept": "application/json"},
    )
    assert created.status_code == 201, created.text

    todo_id = created.json()["id"]
    state_manager.track_created("todos", todo_id)
    endpoint = f"/todos/{todo_id}"

    if not todo_exists:
        deleted = api.delete(endpoint)
        assert deleted.status_code == 200, deleted.text

    expected_status = 200 if todo_exists else 404
    before = system_snapshot()

    get_response = api.get(
        endpoint,
        headers={"Accept": accept},
    )
    assert get_response.status_code == expected_status

    head_response = api_client.head(
        f"{api_url}{endpoint}",
        headers={"Accept": accept},
        timeout=5,
    )

    assert head_response.status_code == expected_status
    assert head_response.content == b""

    get_type = get_response.headers.get("Content-Type", "")
    head_type = head_response.headers.get("Content-Type", "")

    assert head_type == get_type

    if todo_exists:
        assert head_type.split(";")[0].strip().lower() == accept

    assert system_snapshot() == before