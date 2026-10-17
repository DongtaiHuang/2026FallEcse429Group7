def test_xml_should_create_todo_category_relationship(
    api_client,
    api_url,
    entity_factory,
    state_manager,
    system_snapshot,
):
    todo = entity_factory("todos")
    category = entity_factory("categories")

    todo_id = todo["id"]
    category_id = category["id"]
    before = system_snapshot()

    response = api_client.post(
        f"{api_url}/todos/{todo_id}/categories",
        data=(
            f"<category><id>{category_id}</id></category>"
        ).encode("utf-8"),
        headers={
            "Content-Type": "application/xml",
            "Accept": "application/json",
        },
        timeout=5,
    )

    if response.status_code == 201:
        state_manager.track_relationship(
            "todos", todo_id, "categories", category_id
        )

    assert response.status_code == 201, response.text
    assert response.content == b""

    before["todos"][todo_id]["categories"] = [
        {"id": category_id}
    ]
    assert system_snapshot() == before