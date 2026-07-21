"""Tests for Phase-2 entity existence rules."""

from custom_components.dashboard_entity_checker.coordinator import _find_missing_entities


class FakeLookup:
    """Minimal state-machine or registry lookup."""

    def __init__(self, existing: set[str]) -> None:
        self.existing = existing

    def get(self, entity_id: str):
        """Return an object when the state exists."""
        return object() if entity_id in self.existing else None

    def async_get(self, entity_id: str):
        """Return an object when the registry entry exists."""
        return object() if entity_id in self.existing else None


def test_only_entities_unknown_to_state_machine_and_registry_are_missing() -> None:
    """Unavailable states and registry-only entities still count as existing."""
    entities = {
        "sensor.available": ["Home"],
        "sensor.unavailable": ["Home"],
        "sensor.registry_only": ["Details"],
        "media_player.echo_bad": ["Home"],
    }
    states = FakeLookup({"sensor.available", "sensor.unavailable"})
    registry = FakeLookup({"sensor.available", "sensor.registry_only"})

    assert _find_missing_entities(entities, states, registry) == [
        {"entity": "media_player.echo_bad", "views": ["Home"]}
    ]
