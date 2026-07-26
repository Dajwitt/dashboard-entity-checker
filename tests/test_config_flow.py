"""Tests for complete config and options flow behavior."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.selector import BooleanSelector, SelectSelector

from custom_components.dashboard_entity_checker.config_flow import (
    DashboardEntityCheckerConfigFlow,
    DashboardEntityCheckerOptionsFlow,
    _get_dashboards,
    _ignored_entity_options,
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
    DOMAIN,
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


def test_form_helpers_preserve_missing_dashboard_selection() -> None:
    """Unavailable dashboards remain selectable."""
    dashboards = {"one": "One"}
    _include_unavailable_selections(dashboards, ["one", "deleted"])

    assert dashboards == {"one": "One", "deleted": "deleted"}


def test_ignore_options_tolerate_incomplete_scan_data() -> None:
    """All HA entities are offered despite incomplete coordinator findings."""
    hass = SimpleNamespace(
        data={
            er.DATA_REGISTRY: SimpleNamespace(
                entities={
                    "button.registry_only": object(),
                    "sensor.shared": object(),
                }
            ),
            DOMAIN: {
                "entry-1": SimpleNamespace(
                    data={
                        "missing_entities": {},
                        "ignored_matches": [
                            None,
                            {"entity": 4},
                            {"entity": "sensor.valid_finding"},
                        ],
                    }
                )
            },
        },
        states=SimpleNamespace(
            async_entity_ids=lambda: ["light.current_state", "sensor.shared"]
        ),
    )

    with patch.object(er, "async_get", return_value=hass.data[er.DATA_REGISTRY]):
        assert _ignored_entity_options(
            hass,
            "entry-1",
            {CONF_IGNORED_ENTITIES: "sensor.configured"},
        ) == [
            "button.registry_only",
            "light.current_state",
            "sensor.configured",
            "sensor.shared",
            "sensor.valid_finding",
        ]

        hass.data[DOMAIN]["entry-1"].data = ["unexpected"]
        assert _ignored_entity_options(
            hass,
            "entry-1",
            {CONF_IGNORED_ENTITIES: "sensor.configured"},
        ) == [
            "button.registry_only",
            "light.current_state",
            "sensor.configured",
            "sensor.shared",
        ]


def _schema_field(result, key):
    """Return a form marker and validator by schema key."""
    for marker, validator in result["data_schema"].schema.items():
        if marker.schema == key:
            return marker, validator
    raise AssertionError(f"Missing schema field: {key}")


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
            er.DATA_REGISTRY: SimpleNamespace(entities={}),
            "lovelace": SimpleNamespace(
                dashboards={
                    "one": SimpleNamespace(config={"title": "One"})
                }
            )
        },
        states=SimpleNamespace(async_entity_ids=list),
    )
    valid = {
        CONF_DASHBOARDS: ["one"],
        CONF_SCAN_INTERVAL: 10,
        CONF_NOTIFICATIONS: False,
        CONF_IGNORED_ENTITIES: ["sensor.ignored"],
    }

    with (
        patch.object(flow, "_async_current_entries", return_value=[]),
        patch.object(er, "async_get", return_value=flow.hass.data[er.DATA_REGISTRY]),
    ):
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
async def test_user_flow_uses_modern_ignore_and_notification_selectors() -> None:
    """Setup offers every state and registry entity in the searchable selector."""
    flow = DashboardEntityCheckerConfigFlow()
    flow.hass = SimpleNamespace(
        data={
            er.DATA_REGISTRY: SimpleNamespace(
                entities={"button.registry_only": object()}
            )
        },
        states=SimpleNamespace(
            async_entity_ids=lambda: ["light.current_state"]
        ),
    )

    with (
        patch.object(flow, "_async_current_entries", return_value=[]),
        patch.object(er, "async_get", return_value=flow.hass.data[er.DATA_REGISTRY]),
    ):
        result = await flow.async_step_user()

    _, notifications = _schema_field(result, CONF_NOTIFICATIONS)
    ignored_marker, ignored_entities = _schema_field(
        result, CONF_IGNORED_ENTITIES
    )

    assert isinstance(notifications, BooleanSelector)
    assert isinstance(ignored_entities, SelectSelector)
    assert ignored_entities.config["options"] == [
        "button.registry_only",
        "light.current_state",
    ]
    assert ignored_entities.config["multiple"] is True
    assert ignored_entities.config["custom_value"] is True
    assert ignored_entities.config["mode"] == "dropdown"
    assert ignored_marker.description == {"suggested_value": []}


@pytest.mark.asyncio
async def test_user_flow_redisplays_validation_errors() -> None:
    """Invalid dashboard and ignore values remain visible in the form."""
    flow = DashboardEntityCheckerConfigFlow()
    flow.hass = SimpleNamespace(
        data={er.DATA_REGISTRY: SimpleNamespace(entities={})},
        states=SimpleNamespace(async_entity_ids=list),
    )
    invalid = {
        CONF_DASHBOARDS: [],
        CONF_SCAN_INTERVAL: 5,
        CONF_NOTIFICATIONS: True,
        CONF_IGNORED_ENTITIES: ["invalid"],
    }

    with (
        patch.object(flow, "_async_current_entries", return_value=[]),
        patch.object(er, "async_get", return_value=flow.hass.data[er.DATA_REGISTRY]),
    ):
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
        options={
            CONF_NOTIFICATIONS: True,
            CONF_IGNORED_ENTITIES: "sensor.old_ignore",
        },
    )
    hass = SimpleNamespace(
        data={
            er.DATA_REGISTRY: SimpleNamespace(
                entities={"button.registry_only": object()}
            ),
            "lovelace": SimpleNamespace(
                dashboards={"one": SimpleNamespace(config={"title": "One"})}
            ),
            "dashboard_entity_checker": {
                "entry-1": SimpleNamespace(
                    data={
                        "missing_entities": [
                            {
                                "entity": "sensor.current_missing",
                                "locations": [],
                            }
                        ],
                        "ignored_matches": [
                            {
                                "entity": "sensor.previously_ignored",
                                "locations": [],
                            }
                        ],
                    }
                )
            },
        },
        states=SimpleNamespace(
            async_entity_ids=lambda: ["light.current_state"]
        ),
        config_entries=_FlowConfigEntries(entry),
    )
    flow = DashboardEntityCheckerOptionsFlow()
    flow.hass = hass
    flow.handler = "entry-1"
    changed = {
        CONF_DASHBOARDS: ["one"],
        CONF_SCAN_INTERVAL: 15,
        CONF_NOTIFICATIONS: False,
        CONF_IGNORED_ENTITIES: ["sensor.ignored"],
    }

    with patch.object(
        er, "async_get", return_value=hass.data[er.DATA_REGISTRY]
    ):
        form = await flow.async_step_init()
    with patch(
        "custom_components.dashboard_entity_checker.config_flow.load_dashboard",
        AsyncMock(return_value={"views": []}),
    ):
        created = await flow.async_step_init(changed)

    assert form["type"] is FlowResultType.FORM
    assert form["step_id"] == "init"
    _, notifications = _schema_field(form, CONF_NOTIFICATIONS)
    ignored_marker, ignored_entities = _schema_field(
        form, CONF_IGNORED_ENTITIES
    )
    assert isinstance(notifications, BooleanSelector)
    assert isinstance(ignored_entities, SelectSelector)
    assert set(ignored_entities.config["options"]) == {
        "button.registry_only",
        "light.current_state",
        "sensor.current_missing",
        "sensor.old_ignore",
        "sensor.previously_ignored",
    }
    assert ignored_marker.description == {
        "suggested_value": ["sensor.old_ignore"]
    }
    assert created["type"] is FlowResultType.CREATE_ENTRY
    assert created["data"] == changed


@pytest.mark.asyncio
async def test_options_flow_can_clear_legacy_ignore_text() -> None:
    """An omitted selector value clears a legacy string setting."""
    entry = SimpleNamespace(
        entry_id="entry-1",
        data={
            CONF_DASHBOARDS: ["one"],
            CONF_SCAN_INTERVAL: 5,
            CONF_IGNORED_ENTITIES: "sensor.old_ignore",
        },
        options={CONF_NOTIFICATIONS: True},
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

    with patch(
        "custom_components.dashboard_entity_checker.config_flow.load_dashboard",
        AsyncMock(return_value={"views": []}),
    ):
        created = await flow.async_step_init(
            {
                CONF_DASHBOARDS: ["one"],
                CONF_SCAN_INTERVAL: 5,
                CONF_NOTIFICATIONS: True,
            }
        )

    assert created["type"] is FlowResultType.CREATE_ENTRY
    assert created["data"][CONF_IGNORED_ENTITIES] == []
