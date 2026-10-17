def test_xml_currently_rejects_existing_todo_id(
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

    assert response.status_code == 404, response.text

    errors = response.json()["errorMessages"]
    assert errors == [
        "Could not find thing matching value for id"
    ]

    assert system_snapshot() == before