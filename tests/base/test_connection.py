
def test_todo_manager_connection(api_client, api_url):
    response = api_client.get(
        f"{api_url}/todos",
        timeout=5
    )

    assert response.status_code == 200

    assert response.headers.get(
        "Content-Type", ""
    ).startswith("application/json")
