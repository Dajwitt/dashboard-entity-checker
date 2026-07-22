"""Tests for Lovelace dashboard access through Home Assistant APIs."""

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from custom_components.dashboard_entity_checker.dashboard import (
    DashboardConfigInvalid,
    DashboardNotFound,
    DashboardNotLoaded,
    get_dashboard_views,
    get_view_names,
    load_dashboard,
)


def _hass_with_dashboard(config):
    dashboard = SimpleNamespace(async_load=AsyncMock(return_value=config))
    hass = SimpleNamespace(
        data={"lovelace": SimpleNamespace(dashboards={"test-dashboard": dashboard})}
    )
    return hass, dashboard


@pytest.mark.asyncio
async def test_load_dashboard_uses_force_reload() -> None:
    """Dashboard changes are loaded through the API with force enabled."""
    config = {"views": [{"title": "Home"}]}
    hass, dashboard = _hass_with_dashboard(config)

    assert await load_dashboard(hass, "test-dashboard") == config
    dashboard.async_load.assert_awaited_once_with(force=True)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "hass",
    [SimpleNamespace(data={}), SimpleNamespace(data={"lovelace": object()})],
)
async def test_load_dashboard_requires_lovelace_registry(hass) -> None:
    """Missing Lovelace data is reported as a load failure."""
    with pytest.raises(DashboardNotLoaded, match="not available"):
        await load_dashboard(hass, "test-dashboard")


@pytest.mark.asyncio
async def test_load_dashboard_reports_missing_dashboard() -> None:
    """An unknown URL path has a dedicated error."""
    hass = SimpleNamespace(
        data={"lovelace": SimpleNamespace(dashboards={})}
    )

    with pytest.raises(DashboardNotFound, match="test-dashboard"):
        await load_dashboard(hass, "test-dashboard")


@pytest.mark.asyncio
async def test_load_dashboard_wraps_api_error() -> None:
    """Errors from LovelaceConfig keep dashboard context."""
    hass, dashboard = _hass_with_dashboard({"views": []})
    dashboard.async_load.side_effect = RuntimeError("storage unavailable")

    with pytest.raises(
        DashboardNotLoaded,
        match="test-dashboard.*storage unavailable",
    ):
        await load_dashboard(hass, "test-dashboard")


@pytest.mark.asyncio
@pytest.mark.parametrize("config", [None, [], "invalid"])
async def test_load_dashboard_rejects_invalid_config(config) -> None:
    """Only a non-empty dictionary is a valid Lovelace config."""
    hass, _dashboard = _hass_with_dashboard(config)

    with pytest.raises(DashboardConfigInvalid, match="empty or not a dict"):
        await load_dashboard(hass, "test-dashboard")


@pytest.mark.asyncio
async def test_dashboard_view_helpers() -> None:
    """View helpers preserve lists and derive readable names."""
    hass, _dashboard = _hass_with_dashboard(
        {
            "views": [
                {"title": "Overview", "path": "home"},
                {"path": "details"},
                {},
            ]
        }
    )

    assert await get_dashboard_views(hass, "test-dashboard") == [
        {"title": "Overview", "path": "home"},
        {"path": "details"},
        {},
    ]
    assert await get_view_names(hass, "test-dashboard") == [
        "Overview",
        "details",
        "(unnamed)",
    ]


@pytest.mark.asyncio
async def test_dashboard_views_rejects_non_list_value() -> None:
    """Malformed views data cannot leak into callers."""
    hass, _dashboard = _hass_with_dashboard({"views": {"title": "Bad"}})

    assert await get_dashboard_views(hass, "test-dashboard") == []
