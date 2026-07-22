"""Tests for config-entry diagnostics."""

from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from custom_components.dashboard_entity_checker.const import DOMAIN, VERSION
from custom_components.dashboard_entity_checker.diagnostics import (
    async_get_config_entry_diagnostics,
)


@pytest.mark.asyncio
async def test_diagnostics_without_coordinator_uses_saved_config() -> None:
    """Diagnostics remain downloadable when setup did not create a coordinator."""
    entry = SimpleNamespace(
        entry_id="entry-1",
        data={"dashboard_url_path": "legacy-dashboard"},
        options={
            "dashboard_url_paths": ["one", "two"],
            "ignored_entities": "sensor.ignored",
        },
    )
    hass = SimpleNamespace(data={DOMAIN: {}})

    result = await async_get_config_entry_diagnostics(hass, entry)

    assert result == {
        "integration_version": VERSION,
        "dashboard": "legacy-dashboard",
        "dashboards": ["one", "two"],
        "last_scan": None,
        "views": [],
        "views_scanned": 0,
        "entities_checked": 0,
        "missing_entities": [],
        "ignored_entities": "sensor.ignored",
        "ignored_matches": [],
        "templates_resolved": {},
        "template_diagnostics": [],
        "last_error": "Coordinator ist nicht verfügbar.",
    }


@pytest.mark.asyncio
async def test_successful_diagnostics_exposes_structured_scan_data() -> None:
    """A successful scan is represented without dropping structured details."""
    scan_time = datetime(2026, 7, 22, 10, 30, tzinfo=timezone.utc)
    coordinator = SimpleNamespace(
        data={
            "dashboard_url": "one",
            "dashboards": ["one", "two"],
            "dashboards_loaded": ["one"],
            "dashboard_errors": [{"dashboard": "two", "error": "not found"}],
            "dashboard_loaded": False,
            "last_scan": scan_time,
            "views": ["Home"],
            "views_scanned": 1,
            "checked_entities": 4,
            "missing_entities": [{"entity": "sensor.missing"}],
            "ignored_entities": ["sensor.ignored"],
            "ignored_matches": [{"entity": "sensor.ignored"}],
            "templates_resolved": {"card": ["Home"]},
            "template_diagnostics": [{"type": "unknown_variable"}],
            "last_error": "Dashboard two konnte nicht geladen werden",
        },
        last_update_success=True,
        last_exception=None,
        dashboard_urls=["one", "two"],
        scan_interval_minutes=5,
        ignored_entities=["fallback.ignored"],
    )
    entry = SimpleNamespace(entry_id="entry-1", data={}, options={})
    hass = SimpleNamespace(data={DOMAIN: {"entry-1": coordinator}})

    result = await async_get_config_entry_diagnostics(hass, entry)

    assert result["integration_version"] == VERSION
    assert result["dashboards"] == ["one", "two"]
    assert result["dashboards_loaded"] == ["one"]
    assert result["dashboard_errors"] == [
        {"dashboard": "two", "error": "not found"}
    ]
    assert result["scan_interval_minutes"] == 5
    assert result["last_scan"] == str(scan_time)
    assert result["entities_checked"] == 4
    assert result["missing_entities"] == [{"entity": "sensor.missing"}]
    assert result["ignored_entities"] == ["sensor.ignored"]
    assert result["templates_resolved"] == {"card": ["Home"]}
    assert result["last_error"] == "Dashboard two konnte nicht geladen werden"


@pytest.mark.asyncio
async def test_failed_diagnostics_prefers_coordinator_exception() -> None:
    """The latest coordinator exception identifies a failed scan."""
    coordinator = SimpleNamespace(
        data=None,
        last_update_success=False,
        last_exception=RuntimeError("scan failed"),
        dashboard_urls=["one"],
        scan_interval_minutes=5,
        ignored_entities=[],
    )
    entry = SimpleNamespace(
        entry_id="entry-1",
        data={"dashboard_url_path": "one"},
        options={},
    )
    hass = SimpleNamespace(data={DOMAIN: {"entry-1": coordinator}})

    result = await async_get_config_entry_diagnostics(hass, entry)

    assert result["dashboard"] == "one"
    assert result["dashboard_loaded"] is False
    assert result["last_scan"] is None
    assert result["last_error"] == "scan failed"
