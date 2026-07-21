"""Dashboard access via Home Assistant Lovelace interface.

Never touches .storage directly. Uses only the official Lovelace API.
"""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


class DashboardError(Exception):
    """Base exception for dashboard access errors."""


class DashboardNotFound(DashboardError):
    """Dashboard with given URL path does not exist."""


class DashboardNotLoaded(DashboardError):
    """Dashboard exists but could not be loaded."""


class DashboardConfigInvalid(DashboardError):
    """Dashboard config is missing or malformed."""


async def load_dashboard(hass: HomeAssistant, url_path: str) -> dict[str, Any]:
    """Load a Lovelace dashboard config via the official API.

    Args:
        hass: Home Assistant instance.
        url_path: Dashboard URL path (e.g. "my-ha-dashboard").

    Returns:
        Dashboard configuration as a dict.

    Raises:
        DashboardNotFound: Dashboard does not exist.
        DashboardNotLoaded: Dashboard could not be loaded.
        DashboardConfigInvalid: Config is missing or invalid.
    """
    try:
        lovelace_data = hass.data["lovelace"]
        dashboards = lovelace_data.dashboards
    except (KeyError, AttributeError) as exc:
        raise DashboardNotLoaded(
            "Lovelace dashboards not available"
        ) from exc

    # Get dashboard by URL path
    dashboard = dashboards.get(url_path)

    if dashboard is None:
        raise DashboardNotFound(
            f"Dashboard '{url_path}' not found"
        )

    # Load config through LovelaceConfig. ``force=True`` ensures dashboard
    # changes are visible immediately and avoids reading .storage directly.
    try:
        config = await dashboard.async_load(force=True)
    except Exception as exc:
        raise DashboardNotLoaded(
            f"Dashboard '{url_path}' could not be loaded: {exc}"
        ) from exc

    if not config or not isinstance(config, dict):
        raise DashboardConfigInvalid(
            f"Dashboard '{url_path}' config is empty or not a dict"
        )

    return config


async def get_dashboard_views(hass: HomeAssistant, url_path: str) -> list[dict[str, Any]]:
    """Load a dashboard and return its views.

    Args:
        hass: Home Assistant instance.
        url_path: Dashboard URL path.

    Returns:
        List of view dicts (each with 'title' and 'path' keys at minimum).
    """
    config = await load_dashboard(hass, url_path)
    views = config.get("views", [])
    if not isinstance(views, list):
        return []
    return views


async def get_view_names(hass: HomeAssistant, url_path: str) -> list[str]:
    """Get human-readable view names from a dashboard.

    Args:
        hass: Home Assistant instance.
        url_path: Dashboard URL path.

    Returns:
        List of view names (title or path).
    """
    views = await get_dashboard_views(hass, url_path)
    names: list[str] = []
    for view in views:
        name = view.get("title") or view.get("path") or "(unnamed)"
        names.append(name)
    return names
