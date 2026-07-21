"""Dashboard Entity Checker integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
from homeassistant.core import CoreState, Event, HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError

from .const import CONF_DASHBOARD, CONF_DASHBOARDS, DOMAIN
from .coordinator import DashboardEntityCheckerCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Dashboard Entity Checker from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    coordinator = DashboardEntityCheckerCoordinator(
        hass,
        {**entry.data, **entry.options},
        config_entry=entry,
    )
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register scan_now service
    async def handle_scan_now(call: ServiceCall) -> None:
        """Handle the scan_now service call."""
        await coordinator.async_refresh()
        if not coordinator.last_update_success:
            raise HomeAssistantError(str(coordinator.last_exception))

    hass.services.async_register(DOMAIN, "scan_now", handle_scan_now)

    if _is_home_assistant_fully_started(hass.state):
        await coordinator.async_start_scanning()
    else:
        start_listener_consumed = False

        async def _async_start_scanning(_event: Event) -> None:
            """Start the initial and periodic scans after HA startup."""
            nonlocal start_listener_consumed
            start_listener_consumed = True
            await coordinator.async_start_scanning()

        remove_start_listener = hass.bus.async_listen_once(
            EVENT_HOMEASSISTANT_STARTED, _async_start_scanning
        )

        def _remove_pending_start_listener() -> None:
            """Remove the listener only if its one-time event has not fired."""
            nonlocal start_listener_consumed
            if start_listener_consumed:
                return
            start_listener_consumed = True
            remove_start_listener()

        entry.async_on_unload(_remove_pending_start_listener)

    entry.async_on_unload(entry.add_update_listener(async_update_options))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
        hass.services.async_remove(DOMAIN, "scan_now")

    return unload_ok


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


def _is_home_assistant_fully_started(state: CoreState) -> bool:
    """Return whether the complete Home Assistant startup has finished."""
    return state is CoreState.running


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate the legacy single-dashboard setting to a list."""
    if entry.version >= 2:
        return True

    data = dict(entry.data)
    options = dict(entry.options)
    legacy_data = data.pop(CONF_DASHBOARD, None)
    legacy_options = options.pop(CONF_DASHBOARD, None)
    if CONF_DASHBOARDS not in data and legacy_data:
        data[CONF_DASHBOARDS] = [legacy_data]
    if CONF_DASHBOARDS not in options and legacy_options:
        options[CONF_DASHBOARDS] = [legacy_options]

    hass.config_entries.async_update_entry(
        entry, data=data, options=options, version=2
    )
    return True
