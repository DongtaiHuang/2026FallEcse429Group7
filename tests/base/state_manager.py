
class StateManager:
    """Track test changes and undo them after execution."""

    def __init__(self, api):
        self.api = api
        self.undo_actions = []

    def track_created(self, entity_type, entity_id):
        """Register a newly created object for deletion."""
        valid_types = ("todos", "projects", "categories")

        if entity_type not in valid_types:
            raise ValueError(f"Invalid entity type: {entity_type}")

        def undo():
            response = self.api.delete(
                f"/{entity_type}/{entity_id}"
            )

            if response.status_code not in (200, 204, 404):
                raise AssertionError(
                    f"Failed to delete {entity_type}/{entity_id}: "
                    f"HTTP {response.status_code}"
                )

        self.undo_actions.append(undo)

    def register_undo(self, action):
        """Register an operation that restores a prior change."""
        if not callable(action):
            raise TypeError("Undo action must be callable")

        self.undo_actions.append(action)
    
    
    def track_update(self, entity_type, entity_id):
        """Save an entity's current values for restoration."""
        if entity_type not in ("todos", "projects", "categories"):
            raise ValueError(f"Invalid entity type: {entity_type}")

        response = self.api.get(
            f"/{entity_type}/{entity_id}"
        )
        response.raise_for_status()

        entities = response.json()[entity_type]

        if len(entities) != 1:
            raise AssertionError("Expected exactly one entity")

        original = entities[0].copy()

        def undo():
            payload = {
                key: value
                for key, value in original.items()
                if key != "id"
            }

            if entity_type == "todos":
                status = payload.get("doneStatus")

                if isinstance(status, str):
                    if status.lower() == "true":
                        payload["doneStatus"] = True
                    elif status.lower() == "false":
                        payload["doneStatus"] = False

            result = self.api.put(
                f"/{entity_type}/{entity_id}",
                data=payload
            )

            if not 200 <= result.status_code < 300:
                raise AssertionError(
                    f"Failed to restore {entity_type}/{entity_id}: "
                    f"HTTP {result.status_code}: {result.text}"
                )

        # IMPORTANT: Outside undo(), but inside track_update().
        self.undo_actions.append(undo)


    def track_relationship(self, parent_type, parent_id,
                           relation_type, child_id):
        """Register cleanup for a newly created relationship."""

        valid_types = ("todos", "projects", "categories")

        if parent_type not in valid_types:
            raise ValueError(f"Invalid parent type: {parent_type}")

        if relation_type not in ("categories", "tasks", "tasksof", "todos"):
            raise ValueError(f"Invalid relationship type: {relation_type}")

        endpoint = (
            f"/{parent_type}/{parent_id}/"
            f"{relation_type}/{child_id}"
        )

        def undo():
            response = self.api.delete(endpoint)

            if response.status_code not in (200, 204, 404):
                raise AssertionError(
                    f"Failed to remove relationship {endpoint}: "
                    f"HTTP {response.status_code}: {response.text}"
                )

        self.undo_actions.append(undo)


    def track_deleted_relationship(
        self, parent_type, parent_id, relation_type, child_id
    ):
        """Register recreation of a relationship removed by a test."""

        valid_types = ("todos", "projects", "categories")
        if parent_type not in valid_types:
            raise ValueError(f"Invalid parent type: {parent_type}")

        endpoint = f"/{parent_type}/{parent_id}/{relation_type}"

        def undo():
            response = self.api.post(
                endpoint,
                data={"id": child_id}
            )

            if not 200 <= response.status_code < 300:
                raise AssertionError(
                    f"Failed to restore relationship at {endpoint}: "
                    f"HTTP {response.status_code}: {response.text}"
                )

        self.undo_actions.append(undo)

    def restore(self):
        """Attempt all undo actions in reverse order."""
        errors = []

        for action in reversed(self.undo_actions):
            try:
                action()
            except Exception as error:
                errors.append(str(error))

        self.undo_actions.clear()

        if errors:
            raise AssertionError(
                "State restoration failed:\n" +
                "\n".join(errors)
            )
