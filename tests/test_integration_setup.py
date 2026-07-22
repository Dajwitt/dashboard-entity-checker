"""Tests for integration setup, unload, services and sensor platform."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.core import CoreState
from homeassistant.exceptions import HomeAssistantError

from custom_components.dashboard_entity_checker import (
    async_migrate_entry,
    async_setup_entry,
    async_unload_entry,
    async_update_options,
)
from custom_components.dashboard_entity_checker.const import DOMAIN, VERSION
from custom_components.dashboard_entity_checker.sensor import (
    DashboardEntityCheckerSensor,
    async_setup_entry as async_setup_sensor_entry,
)


def _entry() -> SimpleNamespace:
    return SimpleNamespace(
        entry_id="entry-1",
        data={"dashboard_url_paths": ["one"]},
        options={"scan_interval": 5},
        add_update_listener=MagicMock(return_value=MagicMock()),
        async_on_unload=MagicMock(),
    )


def _hass(state=CoreState.running) -> SimpleNamespace:
    return SimpleNamespace(
        data={},
        state=state,
        config_entries=SimpleNamespace(
            async_forward_entry_setups=AsyncMock(),
            async_unload_platforms=AsyncMock(return_value=True),
            async_reload=AsyncMock(),
            async_update_entry=MagicMock(),
        ),
        services=SimpleNamespace(
            async_register=MagicMock(),
            async_remove=MagicMock(),
        ),
        bus=SimpleNamespace(async_listen_once=MagicMock()),
    )


def _coordinator() -> SimpleNamespace:
    return SimpleNamespace(
        async_start_scanning=AsyncMock(),
        async_refresh=AsyncMock(),
        last_update_success=True,
        last_exception=None,
    )


@pytest.mark.asyncio
async def test_setup_running_core_registers_service_and_starts_scan() -> None:
    """A fully started HA instance scans immediately and exposes scan_now."""
    hass = _hass()
    entry = _entry()
    coordinator = _coordinator()

    with patch(
        "custom_components.dashboard_entity_checker.DashboardEntityCheckerCoordinator",
        return_value=coordinator,
    ):
        assert await async_setup_entry(hass, entry)

    assert hass.data[DOMAIN][entry.entry_id] is coordinator
    hass.config_entries.async_forward_entry_setups.assert_awaited_once_with(
        entry, ["sensor"]
    )
    coordinator.async_start_scanning.assert_awaited_once()
    handler = hass.services.async_register.call_args.args[2]
    await handler(SimpleNamespace())
    assert coordinator.async_refresh.await_count == 1
    entry.add_update_listener.assert_called_once()


@pytest.mark.asyncio
async def test_scan_service_raises_when_refresh_fails() -> None:
    """A failed manual scan is visible to service callers."""
    hass = _hass()
    entry = _entry()
    coordinator = _coordinator()
    coordinator.last_update_success = False
    coordinator.last_exception = RuntimeError("scan failed")

    with patch(
        "custom_components.dashboard_entity_checker.DashboardEntityCheckerCoordinator",
        return_value=coordinator,
    ):
        await async_setup_entry(hass, entry)

    handler = hass.services.async_register.call_args.args[2]
    with pytest.raises(HomeAssistantError, match="scan failed"):
        await handler(SimpleNamespace())


@pytest.mark.asyncio
async def test_setup_waits_for_started_event_and_cleanup_is_idempotent() -> None:
    """Startup listener starts once and its unload cleanup is safe afterwards."""
    hass = _hass(CoreState.starting)
    entry = _entry()
    coordinator = _coordinator()
    remove_listener = MagicMock()
    hass.bus.async_listen_once.return_value = remove_listener

    with patch(
        "custom_components.dashboard_entity_checker.DashboardEntityCheckerCoordinator",
        return_value=coordinator,
    ):
        await async_setup_entry(hass, entry)

    coordinator.async_start_scanning.assert_not_awaited()
    start_callback = hass.bus.async_listen_once.call_args.args[1]
    cleanup = entry.async_on_unload.call_args_list[0].args[0]

    await start_callback(SimpleNamespace())
    cleanup()
    cleanup()

    coordinator.async_start_scanning.assert_awaited_once()
    remove_listener.assert_not_called()


@pytest.mark.asyncio
async def test_pending_start_listener_is_removed_on_early_unload() -> None:
    """Unloading before HA start removes the pending one-time listener once."""
    hass = _hass(CoreState.starting)
    entry = _entry()
    coordinator = _coordinator()
    remove_listener = MagicMock()
    hass.bus.async_listen_once.return_value = remove_listener

    with patch(
        "custom_components.dashboard_entity_checker.DashboardEntityCheckerCoordinator",
        return_value=coordinator,
    ):
        await async_setup_entry(hass, entry)

    cleanup = entry.async_on_unload.call_args_list[0].args[0]
    cleanup()
    cleanup()
    remove_listener.assert_called_once_with()


@pytest.mark.asyncio
@pytest.mark.parametrize("unload_ok", [True, False])
async def test_unload_entry_respects_platform_result(unload_ok) -> None:
    """Runtime data and service are removed only after successful unload."""
    hass = _hass()
    entry = _entry()
    hass.data = {DOMAIN: {entry.entry_id: object()}}
    hass.config_entries.async_unload_platforms.return_value = unload_ok

    assert await async_unload_entry(hass, entry) is unload_ok

    if unload_ok:
        assert entry.entry_id not in hass.data[DOMAIN]
        hass.services.async_remove.assert_called_once_with(DOMAIN, "scan_now")
    else:
        assert entry.entry_id in hass.data[DOMAIN]
        hass.services.async_remove.assert_not_called()


@pytest.mark.asyncio
async def test_options_update_reloads_entry() -> None:
    """Saved options take effect through one config-entry reload."""
    hass = _hass()
    entry = _entry()

    await async_update_options(hass, entry)

    hass.config_entries.async_reload.assert_awaited_once_with(entry.entry_id)


@pytest.mark.asyncio
async def test_current_entry_needs_no_migration() -> None:
    """Version-two entries are left untouched."""
    hass = _hass()
    entry = SimpleNamespace(version=2)

    assert await async_migrate_entry(hass, entry)
    hass.config_entries.async_update_entry.assert_not_called()


@pytest.mark.asyncio
async def test_sensor_platform_adds_configured_entity() -> None:
    """The platform creates exactly one sensor for its coordinator."""
    hass = _hass()
    entry = _entry()
    coordinator = MagicMock()
    hass.data = {DOMAIN: {entry.entry_id: coordinator}}
    add_entities = MagicMock()

    await async_setup_sensor_entry(hass, entry, add_entities)

    entities = add_entities.call_args.args[0]
    assert len(entities) == 1
    assert isinstance(entities[0], DashboardEntityCheckerSensor)
    assert entities[0].unique_id == f"{DOMAIN}_{entry.entry_id}"
    assert entities[0].device_info["sw_version"] == VERSION


def test_sensor_value_and_attributes_follow_coordinator() -> None:
    """The sensor exposes missing count and complete coordinator details."""
    coordinator = MagicMock()
    coordinator.data = None
    coordinator.last_update_success = True
    coordinator.dashboard_url = "one"
    coordinator.dashboard_urls = ["one", "two"]
    coordinator.scan_interval_minutes = 5
    coordinator.ignored_entities = ["sensor.ignored"]
    entry = _entry()
    sensor = DashboardEntityCheckerSensor(coordinator, entry)

    assert sensor.native_value == 0

    coordinator.data = {
        "missing_entities": [{"entity": "sensor.one"}, {"entity": "sensor.two"}],
        "dashboards": ["one", "two"],
        "dashboard_loaded": True,
        "status": "OK",
    }
    assert sensor.native_value == 2
    assert sensor.extra_state_attributes["dashboards"] == ["one", "two"]
    assert sensor.extra_state_attributes["ignored_entities"] == ["sensor.ignored"]
