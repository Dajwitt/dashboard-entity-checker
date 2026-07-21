"""Tests for Phase-6 automatic scan scheduling and diagnostics."""

import asyncio
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.core import CoreState
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.dashboard_entity_checker import _is_home_assistant_fully_started
from custom_components.dashboard_entity_checker.coordinator import (
    DashboardEntityCheckerCoordinator,
    _notification_needs_update,
)
from custom_components.dashboard_entity_checker.dashboard import DashboardNotLoaded
from custom_components.dashboard_entity_checker.sensor import _sensor_attributes


def test_initial_scan_waits_for_fully_running_core() -> None:
    """The startup phase is not considered a completed HA start."""
    assert not _is_home_assistant_fully_started(CoreState.not_running)
    assert not _is_home_assistant_fully_started(CoreState.starting)
    assert _is_home_assistant_fully_started(CoreState.running)


@pytest.mark.asyncio
async def test_start_scanning_enables_interval_and_refreshes_once() -> None:
    """Activation starts polling and performs exactly one initial scan."""
    coordinator = object.__new__(DashboardEntityCheckerCoordinator)
    coordinator._scanning_started = False
    coordinator._configured_update_interval = timedelta(minutes=5)
    coordinator._update_interval = None
    coordinator._update_interval_seconds = None
    coordinator.async_refresh = AsyncMock()

    await coordinator.async_start_scanning()
    await coordinator.async_start_scanning()

    assert coordinator.update_interval == timedelta(minutes=5)
    coordinator.async_refresh.assert_awaited_once()


@pytest.mark.asyncio
async def test_coordinator_serializes_parallel_refresh_requests() -> None:
    """DataUpdateCoordinator's refresh lock prevents overlapping scans."""
    hass = SimpleNamespace(loop=asyncio.get_running_loop())
    coordinator = DashboardEntityCheckerCoordinator(
        hass,
        {
            "dashboard_url_path": "my-ha-dashboard",
            "scan_interval": 5,
            "notifications": True,
        },
    )
    active = 0
    maximum_active = 0

    async def update_data() -> dict:
        nonlocal active, maximum_active
        active += 1
        maximum_active = max(maximum_active, active)
        await asyncio.sleep(0.01)
        active -= 1
        return {"missing_entities": []}

    coordinator._async_scan_data = update_data

    await asyncio.gather(
        coordinator.async_refresh(), coordinator.async_refresh()
    )

    assert maximum_active == 1


def test_identical_scan_result_does_not_touch_notification() -> None:
    """Only a first or changed missing-entity result updates the notification."""
    missing = [{"entity": "sensor.missing", "views": ["Home"]}]

    assert _notification_needs_update(None, missing)
    assert not _notification_needs_update(
        {"missing_entities": missing}, missing
    )
    assert _notification_needs_update(
        {"missing_entities": missing}, []
    )


def test_failed_scan_has_clear_sensor_diagnostics() -> None:
    """A loading problem is visible even without successful coordinator data."""
    coordinator = SimpleNamespace(
        data=None,
        dashboard_url="my-ha-dashboard",
        scan_interval_minutes=5,
        last_update_success=False,
        last_exception=RuntimeError(
            "Dashboard my-ha-dashboard konnte nicht geladen werden."
        ),
    )

    assert _sensor_attributes(coordinator) == {
        "dashboard": "my-ha-dashboard",
        "dashboards": ["my-ha-dashboard"],
        "dashboards_loaded": [],
        "dashboard_errors": [],
        "scan_interval_minutes": 5,
        "dashboard_loaded": False,
        "status": "Fehler",
        "missing_entities": [],
        "checked_entities": 0,
        "templates_resolved": 0,
        "template_diagnostics": [],
        "views": [],
        "views_scanned": 0,
        "last_scan": "",
        "last_error": "Dashboard my-ha-dashboard konnte nicht geladen werden.",
    }


@pytest.mark.asyncio
async def test_dashboard_loading_error_is_wrapped_with_clear_context() -> None:
    """Coordinator failures name the affected dashboard in German."""
    hass = SimpleNamespace(loop=asyncio.get_running_loop())
    coordinator = DashboardEntityCheckerCoordinator(
        hass,
        {
            "dashboard_url_path": "my-ha-dashboard",
            "scan_interval": 5,
            "notifications": True,
        },
    )

    with patch(
        "custom_components.dashboard_entity_checker.coordinator.load_dashboard",
        AsyncMock(side_effect=DashboardNotLoaded("Lovelace nicht verfügbar")),
    ):
        with pytest.raises(
            UpdateFailed,
            match="Dashboards konnten nicht geladen werden",
        ):
            await coordinator._async_scan_data()
