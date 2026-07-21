"""DataUpdateCoordinator for Dashboard Entity Checker."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import (
    CONF_DASHBOARD,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)
from .dashboard import DashboardError, load_dashboard
from .parser import parse_dashboard

_LOGGER = logging.getLogger(__name__)


class DashboardEntityCheckerCoordinator(DataUpdateCoordinator[dict]):
    """Load a dashboard and check its direct entity references."""

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
        """Load, parse and check the configured dashboard."""
        try:
            config = await load_dashboard(self.hass, self.dashboard_url)
            parsed = parse_dashboard(config)
            registry = er.async_get(self.hass)

            missing_entities = _find_missing_entities(
                parsed.entities, self.hass.states, registry
            )

            return {
                "dashboard_loaded": True,
                "dashboard_url": self.dashboard_url,
                "views": parsed.views,
                "views_scanned": len(parsed.views),
                "checked_entities": parsed.checked_entities,
                "missing_entities": missing_entities,
                "status": "Fehler gefunden" if missing_entities else "OK",
                "last_scan": dt_util.now().isoformat(),
            }
        except DashboardError as exc:
            raise UpdateFailed(str(exc)) from exc


def _find_missing_entities(
    entities: dict[str, list[str]], states, registry
) -> list[dict[str, object]]:
    """Return IDs absent from both the state machine and entity registry."""
    return [
        {"entity": entity_id, "views": views}
        for entity_id, views in entities.items()
        if states.get(entity_id) is None and registry.async_get(entity_id) is None
    ]
