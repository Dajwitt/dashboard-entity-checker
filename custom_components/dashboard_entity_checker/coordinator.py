"""DataUpdateCoordinator for Dashboard Entity Checker."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import asdict
from datetime import timedelta
from typing import TypedDict

from homeassistant.components import persistent_notification
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import (
    CONF_DASHBOARD,
    CONF_NOTIFICATIONS,
    CONF_SCAN_INTERVAL,
    DEFAULT_NOTIFICATIONS,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    NOTIFICATION_ID,
)
from .dashboard import DashboardError, load_dashboard
from .parser import parse_dashboard

_LOGGER = logging.getLogger(__name__)


class MissingEntity(TypedDict):
    """A missing entity and the dashboard views using it."""

    entity: str
    views: list[str]


class DashboardEntityCheckerCoordinator(DataUpdateCoordinator[dict]):
    """Load a dashboard and check its direct entity references."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry_data: dict,
        *,
        config_entry: ConfigEntry | None = None,
    ) -> None:
        """Initialize the coordinator."""
        self.dashboard_url = entry_data[CONF_DASHBOARD]
        self.notifications_enabled = entry_data.get(
            CONF_NOTIFICATIONS, DEFAULT_NOTIFICATIONS
        )
        scan_interval = entry_data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        self.scan_interval_minutes = scan_interval
        self._configured_update_interval = timedelta(minutes=scan_interval)
        self._scanning_started = False
        self._scan_lock = asyncio.Lock()

        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name=DOMAIN,
            update_interval=None,
        )

    async def async_start_scanning(self) -> None:
        """Enable periodic polling and perform the first post-start scan."""
        if self._scanning_started:
            return
        self._scanning_started = True
        self.update_interval = self._configured_update_interval
        await self.async_refresh()

    async def _async_update_data(self) -> dict:
        """Serialize all scheduled and manual scan requests."""
        async with self._scan_lock:
            return await self._async_scan_data()

    async def _async_scan_data(self) -> dict:
        """Load, parse and check the configured dashboard."""
        try:
            config = await load_dashboard(self.hass, self.dashboard_url)
            parsed = parse_dashboard(config)
            registry = er.async_get(self.hass)

            missing_entities = _find_missing_entities(
                parsed.entities, self.hass.states, registry
            )
            if _notification_needs_update(self.data, missing_entities):
                _update_notification(
                    self.hass,
                    self.dashboard_url,
                    missing_entities,
                    self.notifications_enabled,
                )

            return {
                "dashboard_loaded": True,
                "dashboard_url": self.dashboard_url,
                "views": parsed.views,
                "views_scanned": len(parsed.views),
                "checked_entities": parsed.checked_entities,
                "missing_entities": missing_entities,
                "templates_resolved": parsed.templates,
                "templates_resolved_count": len(parsed.templates),
                "template_diagnostics": [
                    asdict(diagnostic) for diagnostic in parsed.diagnostics
                ],
                "status": "Fehler gefunden" if missing_entities else "OK",
                "last_scan": dt_util.now().isoformat(),
            }
        except DashboardError as exc:
            raise UpdateFailed(
                f"Dashboard {self.dashboard_url} konnte nicht geladen werden: {exc}"
            ) from exc


def _find_missing_entities(
    entities: dict[str, list[str]], states, registry
) -> list[MissingEntity]:
    """Return IDs absent from both the state machine and entity registry."""
    return [
        {"entity": entity_id, "views": views}
        for entity_id, views in entities.items()
        if states.get(entity_id) is None and registry.async_get(entity_id) is None
    ]


def _notification_needs_update(
    previous_data: dict | None,
    missing_entities: list[MissingEntity],
) -> bool:
    """Return whether the persistent notification content has changed."""
    return (
        previous_data is None
        or previous_data.get("missing_entities") != missing_entities
    )


def _update_notification(
    hass: HomeAssistant,
    dashboard: str,
    missing_entities: list[MissingEntity],
    enabled: bool,
) -> None:
    """Create, update or dismiss the single persistent notification."""
    if not enabled or not missing_entities:
        persistent_notification.async_dismiss(hass, NOTIFICATION_ID)
        return

    persistent_notification.async_create(
        hass,
        _notification_message(missing_entities),
        title=f"Dashboard-Fehler: {dashboard}",
        notification_id=NOTIFICATION_ID,
    )


def _notification_message(missing_entities: list[MissingEntity]) -> str:
    """Build a readable notification body with entity and view names."""
    blocks: list[str] = []
    for item in missing_entities:
        entity_id = item["entity"]
        views = item["views"]
        view_lines = [f"- Ansicht: {view}" for view in views]
        blocks.append("\n".join([entity_id, *view_lines]))
    return "\n\n".join(blocks)
