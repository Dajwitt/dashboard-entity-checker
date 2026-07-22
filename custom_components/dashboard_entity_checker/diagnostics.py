"""Diagnostics support for Dashboard Entity Checker."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, VERSION

TO_REDACT = {"access_token", "token", "password"}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = hass.data[DOMAIN].get(entry.entry_id)

    if coordinator is None:
        current = {**entry.data, **entry.options}
        return {
            "integration_version": VERSION,
            "dashboard": current.get("dashboard_url_path", "unknown"),
            "dashboards": current.get("dashboard_url_paths", []),
            "last_scan": None,
            "views": [],
            "views_scanned": 0,
            "entities_checked": 0,
            "missing_entities": [],
            "ignored_entities": current.get("ignored_entities", ""),
            "ignored_matches": [],
            "templates_resolved": {},
            "template_diagnostics": [],
            "last_error": "Coordinator ist nicht verfügbar.",
        }

    data = coordinator.data or {}
    failed = not coordinator.last_update_success
    last_error = str(coordinator.last_exception) if failed else data.get("last_error")
    result = {
        "integration_version": VERSION,
        "dashboard": data.get(
            "dashboard_url", entry.data.get("dashboard_url_path", "unknown")
        ),
        "dashboards": data.get("dashboards", coordinator.dashboard_urls),
        "dashboards_loaded": data.get("dashboards_loaded", []),
        "dashboard_errors": data.get("dashboard_errors", []),
        "scan_interval_minutes": coordinator.scan_interval_minutes,
        "dashboard_loaded": False if failed else data.get("dashboard_loaded", False),
        "last_scan": str(data.get("last_scan", "")) or None,
        "views": data.get("views", []),
        "views_scanned": data.get("views_scanned", 0),
        "entities_checked": data.get("checked_entities", 0),
        "missing_entities": data.get("missing_entities", []),
        "ignored_entities": data.get(
            "ignored_entities", coordinator.ignored_entities
        ),
        "ignored_matches": data.get("ignored_matches", []),
        "templates_resolved": data.get("templates_resolved", {}),
        "template_diagnostics": data.get("template_diagnostics", []),
        "last_error": last_error,
    }
    return async_redact_data(result, TO_REDACT)
