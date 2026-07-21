"""Tests for Phase-7 multi-dashboard support."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.dashboard_entity_checker import async_migrate_entry
from custom_components.dashboard_entity_checker.const import (
    CONF_DASHBOARD,
    CONF_DASHBOARDS,
    CONF_NOTIFICATIONS,
    CONF_SCAN_INTERVAL,
)
from custom_components.dashboard_entity_checker.coordinator import (
    DashboardEntityCheckerCoordinator,
    _configured_dashboard_urls,
    _find_missing_entities,
    _merge_entity_references,
    _notification_message,
)
from custom_components.dashboard_entity_checker.dashboard import DashboardNotLoaded
from custom_components.dashboard_entity_checker.config_flow import _dashboard_schema


class FakeLookup:
    """Minimal state-machine or registry lookup."""

    def __init__(self, existing: set[str]) -> None:
        self.existing = existing

    def get(self, entity_id: str):
        """Return an object when a state exists."""
        return object() if entity_id in self.existing else None

    def async_get(self, entity_id: str):
        """Return an object when a registry entry exists."""
        return object() if entity_id in self.existing else None


def test_legacy_single_dashboard_config_remains_supported() -> None:
    """Version-1 scalar configuration is normalized to one dashboard."""
    assert _configured_dashboard_urls(
        {CONF_DASHBOARD: "my-ha-dashboard"}
    ) == ["my-ha-dashboard"]


def test_multiple_dashboard_config_is_deduplicated_in_user_order() -> None:
    """Empty and duplicate selections cannot create duplicate scans."""
    assert _configured_dashboard_urls(
        {
            CONF_DASHBOARDS: [
                "my-ha-dashboard",
                "dashboard-test",
                "my-ha-dashboard",
                "",
            ]
        }
    ) == ["my-ha-dashboard", "dashboard-test"]


def test_config_schema_accepts_multiple_selected_dashboards() -> None:
    """The HA selector returns a validated list, not a scalar value."""
    schema = _dashboard_schema(
        {
            "my-ha-dashboard": "MY HA DASHBOARD",
            "dashboard-test": "Test Dashboard",
        },
        ["my-ha-dashboard"],
        5,
        True,
    )

    assert schema(
        {
            CONF_DASHBOARDS: ["my-ha-dashboard", "dashboard-test"],
            CONF_SCAN_INTERVAL: 10,
            CONF_NOTIFICATIONS: False,
        }
    ) == {
        CONF_DASHBOARDS: ["my-ha-dashboard", "dashboard-test"],
        CONF_SCAN_INTERVAL: 10,
        CONF_NOTIFICATIONS: False,
    }


def test_same_entity_groups_dashboard_and_view_locations() -> None:
    """One entity result can point to views in multiple dashboards."""
    references = {}
    _merge_entity_references(
        references,
        "my-ha-dashboard",
        {
            "sensor.shared_missing": ["Wetter"],
            "sensor.available": ["Home"],
        },
    )
    _merge_entity_references(
        references,
        "dashboard-test",
        {
            "sensor.shared_missing": ["Home", "Details"],
            "sensor.registry_only": ["Home"],
        },
    )

    missing = _find_missing_entities(
        references,
        FakeLookup({"sensor.available"}),
        FakeLookup({"sensor.registry_only"}),
    )

    assert missing == [
        {
            "entity": "sensor.shared_missing",
            "locations": [
                {"dashboard": "my-ha-dashboard", "views": ["Wetter"]},
                {
                    "dashboard": "dashboard-test",
                    "views": ["Home", "Details"],
                },
            ],
        }
    ]


def test_notification_lists_dashboard_to_view_paths() -> None:
    """The notification matches the project plan's dashboard → view format."""
    missing = [
        {
            "entity": "sensor.shared_missing",
            "locations": [
                {"dashboard": "my-ha-dashboard", "views": ["Wetter"]},
                {"dashboard": "dashboard-test", "views": ["Home", "Bad"]},
            ],
        }
    ]

    assert _notification_message(missing) == (
        "sensor.shared_missing\n"
        "- my-ha-dashboard → Wetter\n"
        "- dashboard-test → Home\n"
        "- dashboard-test → Bad"
    )


@pytest.mark.asyncio
async def test_config_entry_migration_converts_data_and_options() -> None:
    """Existing v1 installations migrate without losing selected settings."""
    entry = SimpleNamespace(
        version=1,
        data={CONF_DASHBOARD: "my-ha-dashboard", "scan_interval": 5},
        options={CONF_DASHBOARD: "dashboard-test", "notifications": False},
    )
    update_entry = MagicMock()
    hass = SimpleNamespace(
        config_entries=SimpleNamespace(async_update_entry=update_entry)
    )

    assert await async_migrate_entry(hass, entry)
    update_entry.assert_called_once_with(
        entry,
        data={CONF_DASHBOARDS: ["my-ha-dashboard"], "scan_interval": 5},
        options={CONF_DASHBOARDS: ["dashboard-test"], "notifications": False},
        version=2,
    )


@pytest.mark.asyncio
async def test_partial_dashboard_failure_keeps_successful_results() -> None:
    """One broken dashboard is diagnosed without discarding good scans."""
    hass = SimpleNamespace(states=FakeLookup({"sensor.available"}))
    coordinator = DashboardEntityCheckerCoordinator(
        hass,
        {
            CONF_DASHBOARDS: ["my-ha-dashboard", "dashboard-broken"],
            "scan_interval": 5,
            "notifications": True,
        },
    )
    parsed = SimpleNamespace(
        entities={"sensor.available": ["Home"]},
        views=["Home"],
        templates={"tile": ["Home"]},
        diagnostics=(),
    )

    async def load(_hass, dashboard_url):
        if dashboard_url == "dashboard-broken":
            raise DashboardNotLoaded("Lovelace nicht verfügbar")
        return {"views": []}

    with (
        patch(
            "custom_components.dashboard_entity_checker.coordinator.load_dashboard",
            AsyncMock(side_effect=load),
        ),
        patch(
            "custom_components.dashboard_entity_checker.coordinator.parse_dashboard",
            return_value=parsed,
        ),
        patch(
            "custom_components.dashboard_entity_checker.coordinator.er.async_get",
            return_value=FakeLookup(set()),
        ),
        patch(
            "custom_components.dashboard_entity_checker.coordinator._update_notification"
        ) as update_notification,
    ):
        result = await coordinator._async_scan_data()

    assert result["dashboard_loaded"] is False
    assert result["dashboards_loaded"] == ["my-ha-dashboard"]
    assert result["dashboard_errors"] == [
        {
            "dashboard": "dashboard-broken",
            "error": "Lovelace nicht verfügbar",
        }
    ]
    assert result["status"] == "Teilweise fehlgeschlagen"
    assert result["checked_entities"] == 1
    update_notification.assert_not_called()
