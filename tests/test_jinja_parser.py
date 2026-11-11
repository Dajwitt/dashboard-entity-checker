"""Regression coverage for issue #4: Jinja fragments are not entities."""

from typing import Any
from unittest.mock import Mock

import pytest

from custom_components.dashboard_entity_checker.coordinator import (
    EntityReferences,
    _find_missing_entities,
)
from custom_components.dashboard_entity_checker.parser import parse_dashboard

ISSUE_TEMPLATE = """{%- set ns = namespace(ids=[]) %} {%- for state in states.binary_sensor %}
  {%- if 'pollen_munchen_' in state.entity_id and state.entity_id.endswith('_aktiv') and state.state == 'on' %}
    {%- set art = state.entity_id.replace('binary_sensor.pollen_munchen_', '').replace('_aktiv', '') %}
    {%- set ns.ids = ns.ids + ['sensor.pollen_munchen_' ~ art] %}
  {%- endif %}
{%- endfor %} {{ ns.ids }}"""


def dashboard(template: str, card_type: str) -> dict:
    """Use the same template in each affected card context."""
    card: dict[str, Any] = {"type": card_type}
    if card_type == "markdown":
        card["content"] = template
    else:
        card["card"] = {"type": "entities"}
        card["filter"] = {"template": template}
    return {"views": [{"title": "Pollen", "cards": [card]}]}


@pytest.mark.parametrize("card_type", ["custom:auto-entities", "markdown"])
def test_issue_4_original_template(card_type: str) -> None:
    """The exact issue example must not report either runtime prefix."""
    result = parse_dashboard(dashboard(ISSUE_TEMPLATE, card_type))
    assert result.entities == {}
    assert result.diagnostics == ()


@pytest.mark.parametrize("card_type", ["custom:auto-entities", "markdown"])
@pytest.mark.parametrize(
    "expression",
    [
        "'sensor.pollen_munchen_' ~ art",
        '"sensor.pollen_munchen" ~ art',
        "art ~ ('sensor.pollen_munchen')",
        "('sensor.pollen_munchen' + art)",
        "states['sensor.pollen_munchen_' ~ art]",
        "states('sensor.pollen_munchen_' ~ art)",
        "state.entity_id.replace('binary_sensor.pollen_munchen_', '')",
        "state.entity_id.replace('sensor.pollen', 'sensor.other')",
        "'sensor.pollen'.replace('pollen', art)",
        "state.entity_id | replace('sensor.pollen', 'sensor.other')",
        "'sensor.pollen' | replace('pollen', art)",
    ],
)
def test_dynamic_literals_are_not_static_references(
    card_type: str, expression: str
) -> None:
    """Suppression depends on syntax, not an underscore suffix or JS marker."""
    template = (
        "{% for state in states.binary_sensor %}{{ " + expression + " }}{% endfor %}"
    )
    assert parse_dashboard(dashboard(template, card_type)).entities == {}


@pytest.mark.parametrize("card_type", ["custom:auto-entities", "markdown"])
@pytest.mark.parametrize(
    "expression",
    [
        "states('sensor.room_temperature')",
        "is_state('sensor.room_temperature', 'on')",
        "state_attr('sensor.room_temperature', 'unit_of_measurement')",
        "states['sensor.room_temperature'].state",
        "states.sensor.room_temperature.state",
        "['sensor.room_temperature']",
        "ns.ids + ['sensor.room_temperature']",
        "states('sensor.room_temperature') ~ ' degrees'",
        "state.entity_id.replace(states('sensor.room_temperature'), '')",
        "'sensor.room_temperature'",
    ],
)
def test_static_references_survive(card_type: str, expression: str) -> None:
    """Literal IDs and explicit lookups remain checkable, even inside logic."""
    template = ISSUE_TEMPLATE + "{{ " + expression + " }}"
    assert parse_dashboard(dashboard(template, card_type)).entities == {
        "sensor.room_temperature": ["Pollen"]
    }


def test_no_global_underscore_blacklist() -> None:
    """Keep scalar detection, including existing handling of malformed IDs."""
    config = {
        "views": [
            {
                "entities": [
                    "sensor.room_temperature",
                    "sensor.prefix_",
                    "sensor.room.extra",
                ]
            }
        ]
    }
    assert set(parse_dashboard(config).entities) == {
        "sensor.room_temperature",
        "sensor.prefix_",
        "sensor.room.extra",
    }


def test_jinja_comments_and_plain_text_are_not_entity_references() -> None:
    template = "{# states.sensor.comment #} {{ 'Documentation for sensor.not_an_id' }}"
    assert parse_dashboard(dashboard(template, "markdown")).entities == {}


def test_mixed_jinja_and_javascript_keeps_static_javascript() -> None:
    template = (
        ISSUE_TEMPLATE + "\n[[[ return states['sensor.js_temperature'].state; ]]]"
    )
    assert parse_dashboard(dashboard(template, "markdown")).entities == {
        "sensor.js_temperature": ["Pollen"]
    }


@pytest.mark.parametrize("card_type", ["custom:auto-entities", "markdown"])
def test_only_real_missing_static_references_reach_missing_entities(
    card_type: str,
) -> None:
    """Prefix suppression must not hide genuinely missing static references."""
    template = (
        ISSUE_TEMPLATE
        + """
    {{ states('sensor.pollen_munchen_birke') }}
    {{ states['binary_sensor.pollen_munchen_birke_aktiv'].state }}
    {{ states('sensor.really_missing') }}
    """
    )
    parsed = parse_dashboard(dashboard(template, card_type))
    entities: EntityReferences = {
        entity: [{"dashboard": "pollen", "views": views}]
        for entity, views in parsed.entities.items()
    }
    existing = {
        "sensor.pollen_munchen_birke",
        "binary_sensor.pollen_munchen_birke_aktiv",
    }
    states = Mock()
    states.get.side_effect = lambda entity: object() if entity in existing else None
    registry = Mock()
    registry.async_get.return_value = None
    assert _find_missing_entities(entities, states, registry) == [
        {
            "entity": "sensor.really_missing",
            "locations": [{"dashboard": "pollen", "views": ["Pollen"]}],
        }
    ]


@pytest.mark.parametrize("control", ["break", "continue"])
def test_home_assistant_loop_controls_keep_static_references(control: str) -> None:
    template = (
        "{% for state in states.sensor %}{{ states('sensor.room_temperature') }}"
        "{% " + control + " %}{% endfor %}"
    )
    assert parse_dashboard(dashboard(template, "markdown")).entities == {
        "sensor.room_temperature": ["Pollen"]
    }


@pytest.mark.parametrize("key", ["style", "styles", "url", "icon", "type"])
def test_non_entity_fields_only_collect_explicit_jinja_lookups(key: str) -> None:
    config = {
        "views": [
            {key: "{{ 'sensor.not_an_entity' }} {{ states('sensor.temperature') }}"}
        ]
    }
    assert parse_dashboard(config).entities == {"sensor.temperature": ["view_0"]}


def test_static_jinja_literal_with_trailing_underscore_is_not_globally_hidden() -> None:
    assert parse_dashboard(
        dashboard("{{ ['sensor.prefix_'] }}", "markdown")
    ).entities == {"sensor.prefix_": ["Pollen"]}


def test_invalid_jinja_does_not_abort_dashboard_scan() -> None:
    config = dashboard("{{ 'sensor.prefix_' ~ }}", "markdown")
    config["views"][0]["cards"].append({"entity": "light.kitchen"})
    assert parse_dashboard(config).entities == {"light.kitchen": ["Pollen"]}
