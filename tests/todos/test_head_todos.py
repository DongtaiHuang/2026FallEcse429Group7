import pytest


@pytest.mark.parametrize(
    "accept",
    ["application/json", "application/xml"]
)
def test_head_todos_returns_headers_without_body(
    api_client, api_url, accept
):
    headers = {"Accept": accept}

    get_response = api_client.get(
        f"{api_url}/todos",
        headers=headers,
        timeout=5
    )
    assert get_response.status_code == 200

    head_response = api_client.head(
        f"{api_url}/todos",
        headers=headers,
        timeout=5
    )

    assert head_response.status_code == 200
    assert head_response.content == b""

    get_type = get_response.headers.get("Content-Type", "")
    head_type = head_response.headers.get("Content-Type", "")

    assert head_type.split(";")[0].strip().lower() == accept
    assert head_type == get_type