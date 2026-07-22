"""Tests for complete config and options flow behavior."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.data_entry_flow import FlowResultType

from custom_components.dashboard_entity_checker.config_flow import (
    DashboardEntityCheckerConfigFlow,
    DashboardEntityCheckerOptionsFlow,
    _get_dashboards,
    _ignored_entities_text,
    _include_unavailable_selections,
    _selected_dashboard_urls,
    _validate_dashboard_selection,
    _validate_ignored_entities,
)
from custom_components.dashboard_entity_checker.const import (
    CONF_DASHBOARD,
    CONF_DASHBOARDS,
    CONF_IGNORED_ENTITIES,
    CONF_NOTIFICATIONS,
    CONF_SCAN_INTERVAL,
    DEFAULT_DASHBOARD,
)
from custom_components.dashboard_entity_checker.dashboard import DashboardNotFound


class _FlowConfigEntries:
    def __init__(self, entry=None) -> None:
        self.entry = entry

    def async_get_known_entry(self, _entry_id):
        return self.entry


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (None, []),
        ({}, []),
        ({CONF_DASHBOARDS: ["one", "", 4, "two"]}, ["one", "two"]),
        ({CONF_DASHBOARDS: ("one", "two")}, ["one", "two"]),
        ({CONF_DASHBOARD: "legacy"}, ["legacy"]),
        ({CONF_DASHBOARD: ""}, []),
    ],
)
def test_selected_dashboard_urls_handles_current_and_legacy_data(
    data, expected
) -> None:
    """Selections are normalized without inventing invalid values."""
    assert _selected_dashboard_urls(data) == expected


def test_form_helpers_preserve_missing_selection_and_ignore_text() -> None:
    """Unavailable dashboards remain selectable and ignored IDs stay line based."""
    dashboards = {"one": "One"}
    _include_unavailable_selections(dashboards, ["one", "deleted"])

    assert dashboards == {"one": "One", "deleted": "deleted"}
    assert _ignored_entities_text(
        {CONF_IGNORED_ENTITIES: "sensor.two\nsensor.one\nsensor.two"}
    ) == "sensor.two\nsensor.one"


@pytest.mark.asyncio
async def test_get_dashboards_reads_lovelace_metadata() -> None:
    """The selector labels dashboards through LovelaceData metadata."""
    hass = SimpleNamespace(
        data={
            "lovelace": SimpleNamespace(
                dashboards={
                    None: SimpleNamespace(config={"title": "Overview"}),
                    "one": SimpleNamespace(config={"title": "One"}),
                    "two": SimpleNamespace(config={}),
                    "": SimpleNamespace(config={"title": "Ignored"}),
                }
            )
        }
    )

    assert await _get_dashboards(hass) == {"one": "One", "two": "two"}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "hass",
    [
        SimpleNamespace(data={}),
        SimpleNamespace(data={"lovelace": object()}),
        SimpleNamespace(
            data={"lovelace": SimpleNamespace(dashboards={None: object()})}
        ),
    ],
)
async def test_get_dashboards_has_safe_default(hass) -> None:
    """The config flow remains usable before Lovelace metadata is ready."""
    assert await _get_dashboards(hass) == {
        DEFAULT_DASHBOARD: DEFAULT_DASHBOARD
    }


@pytest.mark.asyncio
async def test_dashboard_selection_validation() -> None:
    """Selection validation requires every configured dashboard to load."""
    hass = object()

    assert await _validate_dashboard_selection(hass, {}) == {
        CONF_DASHBOARDS: "no_dashboard_selected"
    }

    with patch(
        "custom_components.dashboard_entity_checker.config_flow.load_dashboard",
        AsyncMock(side_effect=DashboardNotFound("missing")),
    ):
        assert await _validate_dashboard_selection(
            hass, {CONF_DASHBOARDS: ["missing"]}
        ) == {CONF_DASHBOARDS: "dashboard_not_found"}

    load = AsyncMock(return_value={"views": []})
    with patch(
        "custom_components.dashboard_entity_checker.config_flow.load_dashboard",
        load,
    ):
        assert await _validate_dashboard_selection(
            hass, {CONF_DASHBOARDS: ["one", "two"]}
        ) == {}
    assert load.await_count == 2


def test_ignore_validation_accepts_exact_ids_only() -> None:
    """Malformed ignore-list entries are rejected before saving."""
    assert _validate_ignored_entities(
        {CONF_IGNORED_ENTITIES: "sensor.valid\nlight.also_valid"}
    ) == {}
    assert _validate_ignored_entities(
        {CONF_IGNORED_ENTITIES: "not an entity"}
    ) == {CONF_IGNORED_ENTITIES: "invalid_entity_id"}


@pytest.mark.asyncio
async def test_user_flow_aborts_for_existing_entry() -> None:
    """Only one config entry can exist."""
    flow = DashboardEntityCheckerConfigFlow()
    flow.hass = SimpleNamespace()
    with patch.object(flow, "_async_current_entries", return_value=[object()]):
        result = await flow.async_step_user()

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "single_instance_allowed"


@pytest.mark.asyncio
async def test_user_flow_shows_form_then_creates_entry() -> None:
    """The initial flow exposes defaults and saves validated input."""
    flow = DashboardEntityCheckerConfigFlow()
    flow.hass = SimpleNamespace(
        data={
            "lovelace": SimpleNamespace(
                dashboards={
                    "one": SimpleNamespace(config={"title": "One"})
                }
            )
        }
    )
    valid = {
        CONF_DASHBOARDS: ["one"],
        CONF_SCAN_INTERVAL: 10,
        CONF_NOTIFICATIONS: False,
        CONF_IGNORED_ENTITIES: "sensor.ignored",
    }

    with patch.object(flow, "_async_current_entries", return_value=[]):
        form = await flow.async_step_user()
        with patch(
            "custom_components.dashboard_entity_checker.config_flow.load_dashboard",
            AsyncMock(return_value={"views": []}),
        ):
            created = await flow.async_step_user(valid)

    assert form["type"] is FlowResultType.FORM
    assert form["step_id"] == "user"
    assert created["type"] is FlowResultType.CREATE_ENTRY
    assert created["data"] == valid


@pytest.mark.asyncio
async def test_user_flow_redisplays_validation_errors() -> None:
    """Invalid dashboard and ignore values remain visible in the form."""
    flow = DashboardEntityCheckerConfigFlow()
    flow.hass = SimpleNamespace(data={})
    invalid = {
        CONF_DASHBOARDS: [],
        CONF_SCAN_INTERVAL: 5,
        CONF_NOTIFICATIONS: True,
        CONF_IGNORED_ENTITIES: "invalid",
    }

    with patch.object(flow, "_async_current_entries", return_value=[]):
        result = await flow.async_step_user(invalid)

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {
        CONF_DASHBOARDS: "no_dashboard_selected",
        CONF_IGNORED_ENTITIES: "invalid_entity_id",
    }


@pytest.mark.asyncio
async def test_options_flow_uses_current_values_and_saves_changes() -> None:
    """Options use the HA-injected entry and can be updated."""
    entry = SimpleNamespace(
        entry_id="entry-1",
        data={CONF_DASHBOARDS: ["one"], CONF_SCAN_INTERVAL: 5},
        options={CONF_NOTIFICATIONS: True, CONF_IGNORED_ENTITIES: ""},
    )
    hass = SimpleNamespace(
        data={
            "lovelace": SimpleNamespace(
                dashboards={"one": SimpleNamespace(config={"title": "One"})}
            )
        },
        config_entries=_FlowConfigEntries(entry),
    )
    flow = DashboardEntityCheckerOptionsFlow()
    flow.hass = hass
    flow.handler = "entry-1"
    changed = {
        CONF_DASHBOARDS: ["one"],
        CONF_SCAN_INTERVAL: 15,
        CONF_NOTIFICATIONS: False,
        CONF_IGNORED_ENTITIES: "sensor.ignored",
    }

    form = await flow.async_step_init()
    with patch(
        "custom_components.dashboard_entity_checker.config_flow.load_dashboard",
        AsyncMock(return_value={"views": []}),
    ):
        created = await flow.async_step_init(changed)

    assert form["type"] is FlowResultType.FORM
    assert form["step_id"] == "init"
    assert created["type"] is FlowResultType.CREATE_ENTRY
    assert created["data"] == changed
