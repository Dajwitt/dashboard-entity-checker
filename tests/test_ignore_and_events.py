"""Tests for ignore-list filtering and changed-result events."""

from types import SimpleNamespace
from unittest.mock import MagicMock

from custom_components.dashboard_entity_checker.const import EVENT_RESULT_CHANGED
from custom_components.dashboard_entity_checker.coordinator import (
    _configured_ignored_entities,
    _fire_result_changed_event,
    _partition_ignored_entities,
)
from custom_components.dashboard_entity_checker.config_flow import (
    _validate_ignored_entities,
)

MISSING = [
    {
        "entity": "sensor.keep_missing",
        "locations": [
            {"dashboard": "my-ha-dashboard", "views": ["Home"]}
        ],
    },
    {
        "entity": "binary_sensor.ignore_missing",
        "locations": [
            {"dashboard": "dashboard-test", "views": ["Details"]}
        ],
    },
]


def test_ignore_list_accepts_lines_commas_whitespace_and_duplicates() -> None:
    """User-entered exact IDs are normalized deterministically."""
    assert _configured_ignored_entities(
        {
            "ignored_entities": (
                " sensor.keep_missing\n"
                "binary_sensor.ignore_missing, sensor.keep_missing "
            )
        }
    ) == ["sensor.keep_missing", "binary_sensor.ignore_missing"]


def test_ignore_list_rejects_malformed_ids_but_accepts_missing_ids() -> None:
    """The field validates syntax without requiring an entity to exist."""
    assert _validate_ignored_entities(
        {"ignored_entities": "sensor.does_not_exist"}
    ) == {}
    assert _validate_ignored_entities(
        {"ignored_entities": "not an entity"}
    ) == {"ignored_entities": "invalid_entity_id"}


def test_ignored_missing_entities_are_kept_separate_from_active_results() -> None:
    """Ignored ghosts stay visible diagnostically but do not raise alerts."""
    active, ignored = _partition_ignored_entities(
        MISSING, {"binary_sensor.ignore_missing"}
    )

    assert active == [MISSING[0]]
    assert ignored == [MISSING[1]]


def test_first_successful_scan_does_not_fire_change_event() -> None:
    """Startup establishes a baseline instead of emitting a false change."""
    bus = SimpleNamespace(async_fire=MagicMock())
    hass = SimpleNamespace(bus=bus)

    _fire_result_changed_event(
        hass,
        None,
        MISSING,
        ["my-ha-dashboard"],
        "2026-07-22T10:00:00+02:00",
    )

    bus.async_fire.assert_not_called()


def test_changed_result_fires_structured_event() -> None:
    """Added and removed IDs accompany the full changed result."""
    bus = SimpleNamespace(async_fire=MagicMock())
    hass = SimpleNamespace(bus=bus)
    previous = {
        "missing_entities": [MISSING[0]],
        "dashboard_errors": [],
    }

    _fire_result_changed_event(
        hass,
        previous,
        [MISSING[1]],
        ["my-ha-dashboard", "dashboard-test"],
        "2026-07-22T10:05:00+02:00",
    )

    bus.async_fire.assert_called_once_with(
        EVENT_RESULT_CHANGED,
        {
            "dashboards": ["my-ha-dashboard", "dashboard-test"],
            "previous_count": 1,
            "current_count": 1,
            "added_entities": ["binary_sensor.ignore_missing"],
            "removed_entities": ["sensor.keep_missing"],
            "missing_entities": [MISSING[1]],
            "scan_time": "2026-07-22T10:05:00+02:00",
        },
    )


def test_unchanged_or_previous_partial_result_does_not_fire_event() -> None:
    """Repeated and incomplete comparisons cannot create noisy events."""
    bus = SimpleNamespace(async_fire=MagicMock())
    hass = SimpleNamespace(bus=bus)

    _fire_result_changed_event(
        hass,
        {"missing_entities": MISSING, "dashboard_errors": []},
        MISSING,
        ["my-ha-dashboard"],
        "2026-07-22T10:10:00+02:00",
    )
    _fire_result_changed_event(
        hass,
        {
            "missing_entities": [],
            "dashboard_errors": [
                {"dashboard": "dashboard-test", "error": "failed"}
            ],
        },
        MISSING,
        ["my-ha-dashboard"],
        "2026-07-22T10:15:00+02:00",
    )

    bus.async_fire.assert_not_called()
