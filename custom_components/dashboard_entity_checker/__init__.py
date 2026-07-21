"""Dashboard Entity Checker integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
from homeassistant.core import CoreState, Event, HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN
from .coordinator import DashboardEntityCheckerCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Dashboard Entity Checker from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    coordinator = DashboardEntityCheckerCoordinator(
        hass, {**entry.data, **entry.options}
    )
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register scan_now service
    async def handle_scan_now(call: ServiceCall) -> None:
        """Handle the scan_now service call."""
        await coordinator.async_refresh()
        if not coordinator.last_update_success:
            raise HomeAssistantError(
                f"Dashboard {coordinator.dashboard_url} konnte nicht geladen werden."
            )

    hass.services.async_register(DOMAIN, "scan_now", handle_scan_now)

    if _is_home_assistant_fully_started(hass.state):
        await coordinator.async_start_scanning()
    else:

        async def _async_start_scanning(_event: Event) -> None:
            """Start the initial and periodic scans after HA startup."""
            await coordinator.async_start_scanning()

        entry.async_on_unload(
            hass.bus.async_listen_once(
                EVENT_HOMEASSISTANT_STARTED, _async_start_scanning
            )
        )

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
