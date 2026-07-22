"""DataUpdateCoordinator for Dashboard Entity Checker."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import asdict
from datetime import timedelta
from typing import Any, TypedDict

from homeassistant.components import persistent_notification
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import (
    CONF_DASHBOARD,
    CONF_DASHBOARDS,
    CONF_IGNORED_ENTITIES,
    CONF_NOTIFICATIONS,
    CONF_SCAN_INTERVAL,
    DEFAULT_DASHBOARD,
    DEFAULT_IGNORED_ENTITIES,
    DEFAULT_NOTIFICATIONS,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    EVENT_RESULT_CHANGED,
    NOTIFICATION_ID,
)
from .dashboard import DashboardError, load_dashboard
from .parser import parse_dashboard

_LOGGER = logging.getLogger(__name__)


class EntityLocation(TypedDict):
    """Dashboard and views containing an entity reference."""

    dashboard: str
    views: list[str]


class MissingEntity(TypedDict):
    """A missing entity and all dashboard/view locations using it."""

    entity: str
    locations: list[EntityLocation]


EntityReferences = dict[str, list[EntityLocation]]


class DashboardEntityCheckerCoordinator(DataUpdateCoordinator[dict]):
    """Load configured dashboards and check their rendered entity references."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry_data: dict,
        *,
        config_entry: ConfigEntry | None = None,
    ) -> None:
        """Initialize the coordinator."""
        self.dashboard_urls = _configured_dashboard_urls(entry_data)
        # Kept as a compatibility property for existing service/error consumers.
        self.dashboard_url = self.dashboard_urls[0]
        self.notifications_enabled = entry_data.get(
            CONF_NOTIFICATIONS, DEFAULT_NOTIFICATIONS
        )
        self.ignored_entities = _configured_ignored_entities(entry_data)
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
        """Load, parse and aggregate all configured dashboards."""
        references: EntityReferences = {}
        dashboard_views: dict[str, list[str]] = {}
        templates_resolved: dict[str, dict[str, list[str]]] = {}
        template_diagnostics: list[dict[str, Any]] = []
        dashboard_errors: list[dict[str, str]] = []
        dashboards_loaded: list[str] = []

        for dashboard_url in self.dashboard_urls:
            try:
                config = await load_dashboard(self.hass, dashboard_url)
            except DashboardError as exc:
                dashboard_errors.append(
                    {"dashboard": dashboard_url, "error": str(exc)}
                )
                continue

            parsed = parse_dashboard(config)
            dashboards_loaded.append(dashboard_url)
            dashboard_views[dashboard_url] = parsed.views
            templates_resolved[dashboard_url] = parsed.templates
            _merge_entity_references(references, dashboard_url, parsed.entities)
            template_diagnostics.extend(
                {"dashboard": dashboard_url, **asdict(diagnostic)}
                for diagnostic in parsed.diagnostics
            )

        if not dashboards_loaded:
            details = "; ".join(
                f"{item['dashboard']}: {item['error']}"
                for item in dashboard_errors
            )
            raise UpdateFailed(
                f"Dashboards konnten nicht geladen werden: {details}"
            )

        registry = er.async_get(self.hass)
        detected_missing_entities = _find_missing_entities(
            references, self.hass.states, registry
        )
        missing_entities, ignored_matches = _partition_ignored_entities(
            detected_missing_entities, set(self.ignored_entities)
        )
        scan_time = dt_util.now().isoformat()
        # On partial failure, preserve the previous notification. Removing or
        # changing it from incomplete input could hide a real dashboard error.
        if not self.notifications_enabled:
            _update_notification(
                self.hass,
                self.dashboard_urls,
                missing_entities,
                False,
            )
        elif not dashboard_errors and _notification_needs_update(
            self.data, missing_entities
        ):
            _update_notification(
                self.hass,
                self.dashboard_urls,
                missing_entities,
                self.notifications_enabled,
            )

        if not dashboard_errors:
            _fire_result_changed_event(
                self.hass,
                self.data,
                missing_entities,
                self.dashboard_urls,
                scan_time,
            )

        last_error = (
            "; ".join(
                f"Dashboard {item['dashboard']} konnte nicht geladen werden: "
                f"{item['error']}"
                for item in dashboard_errors
            )
            or None
        )
        return {
            "dashboard_loaded": not dashboard_errors,
            "dashboard_url": self.dashboard_url,
            "dashboards": self.dashboard_urls,
            "dashboards_loaded": dashboards_loaded,
            "dashboard_errors": dashboard_errors,
            "views": dashboard_views,
            "views_scanned": sum(len(views) for views in dashboard_views.values()),
            "checked_entities": len(references),
            "missing_entities": missing_entities,
            "ignored_entities": self.ignored_entities,
            "ignored_matches": ignored_matches,
            "templates_resolved": templates_resolved,
            "templates_resolved_count": sum(
                len(templates) for templates in templates_resolved.values()
            ),
            "template_diagnostics": template_diagnostics,
            "status": (
                "Teilweise fehlgeschlagen"
                if dashboard_errors
                else "Fehler gefunden"
                if missing_entities
                else "OK"
            ),
            "last_scan": scan_time,
            "last_error": last_error,
        }


def _configured_dashboard_urls(entry_data: dict) -> list[str]:
    """Normalize new multi-dashboard and legacy scalar configuration."""
    raw_dashboards = entry_data.get(CONF_DASHBOARDS)
    if isinstance(raw_dashboards, (list, tuple)):
        candidates = raw_dashboards
    else:
        candidates = [entry_data.get(CONF_DASHBOARD, DEFAULT_DASHBOARD)]

    result: list[str] = []
    for candidate in candidates:
        if isinstance(candidate, str) and candidate and candidate not in result:
            result.append(candidate)
    return result or [DEFAULT_DASHBOARD]


def _configured_ignored_entities(entry_data: dict) -> list[str]:
    """Normalize exact entity IDs entered as lines or comma-separated text."""
    raw = entry_data.get(CONF_IGNORED_ENTITIES, DEFAULT_IGNORED_ENTITIES)
    if isinstance(raw, (list, tuple)):
        candidates = raw
    elif isinstance(raw, str):
        candidates = raw.replace(",", "\n").splitlines()
    else:
        candidates = []

    result: list[str] = []
    for candidate in candidates:
        entity_id = candidate.strip() if isinstance(candidate, str) else ""
        if entity_id and entity_id not in result:
            result.append(entity_id)
    return result


def _merge_entity_references(
    target: EntityReferences,
    dashboard: str,
    entities: dict[str, list[str]],
) -> None:
    """Merge one parsed dashboard into dashboard-aware entity locations."""
    for entity_id, views in entities.items():
        locations = target.setdefault(entity_id, [])
        location = next(
            (item for item in locations if item["dashboard"] == dashboard),
            None,
        )
        if location is None:
            locations.append({"dashboard": dashboard, "views": list(views)})
            continue
        for view in views:
            if view not in location["views"]:
                location["views"].append(view)


def _find_missing_entities(
    entities: EntityReferences, states, registry
) -> list[MissingEntity]:
    """Return IDs absent from both the state machine and entity registry."""
    return [
        {"entity": entity_id, "locations": locations}
        for entity_id, locations in entities.items()
        if states.get(entity_id) is None and registry.async_get(entity_id) is None
    ]


def _partition_ignored_entities(
    missing_entities: list[MissingEntity], ignored_entities: set[str]
) -> tuple[list[MissingEntity], list[MissingEntity]]:
    """Separate alerting results from configured exact-ID ignore matches."""
    active: list[MissingEntity] = []
    ignored: list[MissingEntity] = []
    for item in missing_entities:
        (ignored if item["entity"] in ignored_entities else active).append(item)
    return active, ignored


def _fire_result_changed_event(
    hass: HomeAssistant,
    previous_data: dict | None,
    missing_entities: list[MissingEntity],
    dashboards: list[str],
    scan_time: str,
) -> None:
    """Fire one event when a complete result changes after the baseline scan."""
    if previous_data is None or previous_data.get("dashboard_errors"):
        return

    previous_missing = previous_data.get("missing_entities", [])
    if previous_missing == missing_entities:
        return

    previous_ids = {item["entity"] for item in previous_missing}
    current_ids = {item["entity"] for item in missing_entities}
    hass.bus.async_fire(
        EVENT_RESULT_CHANGED,
        {
            "dashboards": dashboards,
            "previous_count": len(previous_missing),
            "current_count": len(missing_entities),
            "added_entities": sorted(current_ids - previous_ids),
            "removed_entities": sorted(previous_ids - current_ids),
            "missing_entities": missing_entities,
            "scan_time": scan_time,
        },
    )


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
    dashboards: str | list[str],
    missing_entities: list[MissingEntity],
    enabled: bool,
) -> None:
    """Create, update or dismiss the single persistent notification."""
    if not enabled or not missing_entities:
        persistent_notification.async_dismiss(hass, NOTIFICATION_ID)
        return

    dashboard_urls = [dashboards] if isinstance(dashboards, str) else dashboards
    title = (
        f"Dashboard-Fehler: {dashboard_urls[0]}"
        if len(dashboard_urls) == 1
        else "Dashboard-Fehler"
    )
    persistent_notification.async_create(
        hass,
        _notification_message(missing_entities),
        title=title,
        notification_id=NOTIFICATION_ID,
    )


def _notification_message(missing_entities: list[MissingEntity]) -> str:
    """Build a readable body with dashboard-to-view locations."""
    blocks: list[str] = []
    for item in missing_entities:
        location_lines = [
            f"- {location['dashboard']} → {view}"
            for location in item["locations"]
            for view in location["views"]
        ]
        blocks.append("\n".join([item["entity"], *location_lines]))
    return "\n\n".join(blocks)
