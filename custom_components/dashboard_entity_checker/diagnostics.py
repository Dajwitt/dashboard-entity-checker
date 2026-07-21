"""Diagnostics support for Dashboard Entity Checker."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, VERSION


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = hass.data[DOMAIN].get(entry.entry_id)

    if coordinator is None or coordinator.data is None:
        return {
            "integration_version": VERSION,
            "dashboard": entry.data.get("dashboard_url_path", "unknown"),
            "last_scan": None,
            "views": [],
            "views_scanned": 0,
            "entities_checked": 0,
            "missing_entities": [],
            "templates_resolved": {},
            "template_diagnostics": [],
            "last_error": None,
        }

    data = coordinator.data
    return {
        "integration_version": VERSION,
        "dashboard": data.get("dashboard_url"),
        "last_scan": str(data.get("last_scan", "")),
        "views": data.get("views", []),
        "views_scanned": data.get("views_scanned", 0),
        "entities_checked": data.get("checked_entities", 0),
        "missing_entities": data.get("missing_entities", []),
        "templates_resolved": data.get("templates_resolved", {}),
        "template_diagnostics": data.get("template_diagnostics", []),
        "last_error": data.get("last_error"),
    }
