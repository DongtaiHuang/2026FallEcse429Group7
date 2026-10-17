def test_xml_should_create_category_todo_relationship(
    api_client,
    api_url,
    entity_factory,
    state_manager,
    system_snapshot,
):
    category = entity_factory("categories")
    todo = entity_factory("todos")

    category_id = category["id"]
    todo_id = todo["id"]
    before = system_snapshot()

    response = api_client.post(
        f"{api_url}/categories/{category_id}/todos",
        data=(
            f"<todo><id>{todo_id}</id></todo>"
        ).encode("utf-8"),
        headers={
            "Content-Type": "application/xml",
            "Accept": "application/json",
        },
        timeout=5,
    )

    if response.status_code == 201:
        state_manager.track_relationship(
            "categories", category_id, "todos", todo_id
        )

    assert response.status_code == 201, response.text
    assert response.content == b""

    before["categories"][category_id]["todos"] = [
        {"id": todo_id}
    ]
    assert system_snapshot() == before