from uuid import uuid4
import json

import pytest


def normalize(value):
    if isinstance(value, dict):
        return {
            key: normalize(item)
            for key, item in value.items()
        }

    if isinstance(value, list):
        return sorted(
            [normalize(item) for item in value],
            key=lambda item: json.dumps(item, sort_keys=True)
        )

    return value


@pytest.fixture
def system_snapshot(api):
    def take_snapshot():
        state = {}

        for entity in ("todos", "categories", "projects"):
            response = api.get(
                f"/{entity}",
                headers={"Accept": "application/json"}
            )
            assert response.status_code == 200, response.text

            state[entity] = {
                item["id"]: normalize(item)
                for item in response.json()[entity]
            }

        return state

    return take_snapshot	















@pytest.fixture
def entity_factory(api, state_manager):
    def create(entity_type, **fields):
        payload = {
            "title": f"pytest-{entity_type}-{uuid4().hex}"
        }
        payload.update(fields)

        response = api.post(
            f"/{entity_type}",
            data=payload,
            headers={"Accept": "application/json"},
        )
        assert response.status_code == 201, response.text

        entity = response.json()
        state_manager.track_created(
            entity_type, entity["id"]
        )
        return entity

    return create














@pytest.fixture
def missing_todo_category_probe(
    api, entity_factory, state_manager
):
    owner = entity_factory("todos")
    missing = entity_factory("todos")
    category = entity_factory("categories")

    linked = api.post(
        f"/todos/{owner['id']}/categories",
        data={"id": category["id"]},
        headers={"Accept": "application/json"},
    )
    assert linked.status_code == 201, linked.text

    state_manager.track_relationship(
        "todos", owner["id"], "categories", category["id"]
    )

    deleted = api.delete(f"/todos/{missing['id']}")
    assert deleted.status_code == 200, deleted.text

    return {
        "endpoint": f"/todos/{missing['id']}/categories",
        "category": category,
    }











@pytest.fixture
def relationship_method_paths(
    api, entity_factory, state_manager
):
    todo = entity_factory("todos")
    category = entity_factory("categories")

    links = [
        ("todos", todo["id"], "categories", category["id"]),
        ("categories", category["id"], "todos", todo["id"]),
    ]
    paths = {}

    for parent_type, parent_id, relation, child_id in links:
        collection = f"/{parent_type}/{parent_id}/{relation}"

        created = api.post(
            collection,
            data={"id": child_id},
            headers={"Accept": "application/json"},
        )
        assert created.status_code == 201, created.text

        state_manager.track_relationship(
            parent_type, parent_id, relation, child_id
        )
        paths[parent_type] = f"{collection}/{child_id}"

    return paths