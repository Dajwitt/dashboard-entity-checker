"""DataUpdateCoordinator for Dashboard Entity Checker.

Phase 1: loads dashboard, extracts view names. No entity checking yet.
"""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_DASHBOARD,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)
from .dashboard import (
    DashboardError,
    get_view_names,
    load_dashboard,
)

_LOGGER = logging.getLogger(__name__)


class DashboardEntityCheckerCoordinator(DataUpdateCoordinator[dict]):
    """Coordinator that periodically loads dashboard config and extracts views."""

    def __init__(self, hass: HomeAssistant, entry_data: dict) -> None:
        """Initialize the coordinator."""
        self.dashboard_url = entry_data[CONF_DASHBOARD]
        scan_interval = entry_data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=scan_interval),
        )

    async def _async_update_data(self) -> dict:
        """Fetch dashboard config and extract view names."""
        try:
            config = await load_dashboard(self.hass, self.dashboard_url)
            views = config.get("views", [])
            view_names = [
                v.get("title") or v.get("path") or "(unnamed)"
                for v in views
                if isinstance(v, dict)
            ]

            return {
                "dashboard_loaded": True,
                "dashboard_url": self.dashboard_url,
                "views": view_names,
                "views_scanned": len(view_names),
                "checked_entities": 0,
                "missing_entities": [],
                "status": "OK",
                "last_scan": self.hass.states.get("sensor.date_time"),
            }
        except DashboardError as exc:
            raise UpdateFailed(str(exc)) from exc
