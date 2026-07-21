"""Tests for Phase-5 decluttering-template resolution."""

from custom_components.dashboard_entity_checker.parser import parse_dashboard


def _decluttering_card(template: str, variables=None) -> dict:
    card = {"type": "custom:decluttering-card", "template": template}
    if variables is not None:
        card["variables"] = variables
    return card


def test_simple_template_reports_entity_under_original_view() -> None:
    """The rendered entity belongs to the view, not to the template name."""
    config = {
        "decluttering_templates": {
            "test_tile": {"card": {"type": "tile", "entity": "[[entity]]"}}
        },
        "views": [
            {
                "title": "Wetter",
                "cards": [
                    _decluttering_card(
                        "test_tile",
                        [{"entity": "sensor.absichtlich_falsch"}],
                    )
                ],
            }
        ],
    }

    result = parse_dashboard(config)

    assert result.entities == {"sensor.absichtlich_falsch": ["Wetter"]}
    assert result.templates == {"test_tile": ["Wetter"]}
    assert result.diagnostics == ()


def test_defaults_are_applied_and_explicit_variables_override_them() -> None:
    """Defaults fill missing values while card variables take precedence."""
    config = {
        "decluttering_templates": {
            "dual_tile": {
                "default": [
                    {"primary": "sensor.default_primary"},
                    {"secondary": "sensor.default_secondary"},
                ],
                "card": {
                    "entities": ["[[primary]]", "[[secondary]]"],
                },
            }
        },
        "views": [
            {
                "title": "Home",
                "cards": [
                    _decluttering_card(
                        "dual_tile", [{"primary": "sensor.explicit_primary"}]
                    )
                ],
            }
        ],
    }

    assert parse_dashboard(config).entities == {
        "sensor.default_secondary": ["Home"],
        "sensor.explicit_primary": ["Home"],
    }


def test_nested_templates_preserve_typed_variables_and_view_location() -> None:
    """Nested cards resolve objects and placeholders under the caller's view."""
    config = {
        "decluttering_templates": {
            "outer": {
                "card": _decluttering_card(
                    "inner",
                    [
                        {"entity": "[[outer_entity]]"},
                        {
                            "content": {
                                "type": "entities",
                                "entities": ["[[second_entity]]"],
                            }
                        },
                    ],
                )
            },
            "inner": {
                "card": {
                    "type": "vertical-stack",
                    "cards": [
                        {"entity": "[[entity]]"},
                        "[[content]]",
                    ],
                }
            },
        },
        "views": [
            {
                "title": "Bad",
                "cards": [
                    _decluttering_card(
                        "outer",
                        [
                            {"outer_entity": "sensor.bad_temperature"},
                            {"second_entity": "binary_sensor.bad_window"},
                        ],
                    )
                ],
            }
        ],
    }

    result = parse_dashboard(config)

    assert result.entities == {
        "binary_sensor.bad_window": ["Bad"],
        "sensor.bad_temperature": ["Bad"],
    }
    assert result.templates == {"inner": ["Bad"], "outer": ["Bad"]}
    assert result.diagnostics == ()


def test_same_template_in_multiple_views_groups_entity_locations() -> None:
    """A shared template keeps each calling view as a location."""
    config = {
        "decluttering_templates": {
            "shared": {"card": {"entity": "[[entity]]"}}
        },
        "views": [
            {
                "title": "Home",
                "cards": [
                    _decluttering_card("shared", [{"entity": "sensor.shared"}])
                ],
            },
            {
                "title": "Wetter",
                "cards": [
                    _decluttering_card("shared", [{"entity": "sensor.shared"}])
                ],
            },
        ],
    }

    result = parse_dashboard(config)
    assert result.entities == {"sensor.shared": ["Home", "Wetter"]}
    assert result.templates == {"shared": ["Home", "Wetter"]}


def test_missing_template_produces_diagnostic_without_crashing() -> None:
    """Unknown template names are diagnostics, not parser failures."""
    config = {
        "decluttering_templates": {},
        "views": [
            {
                "title": "Home",
                "cards": [_decluttering_card("does_not_exist")],
            }
        ],
    }

    result = parse_dashboard(config)

    assert result.entities == {}
    assert [diagnostic.code for diagnostic in result.diagnostics] == [
        "missing_template"
    ]
    assert result.diagnostics[0].view == "Home"
    assert result.diagnostics[0].template == "does_not_exist"


def test_unknown_variable_produces_diagnostic_without_false_entity() -> None:
    """Unresolved placeholders stay out of entity results."""
    config = {
        "decluttering_templates": {
            "broken": {"card": {"entity": "[[missing_entity]]"}}
        },
        "views": [
            {"title": "Home", "cards": [_decluttering_card("broken")]}
        ],
    }

    result = parse_dashboard(config)

    assert result.entities == {}
    assert [diagnostic.code for diagnostic in result.diagnostics] == [
        "unknown_variable"
    ]
    assert result.diagnostics[0].variable == "missing_entity"


def test_circular_templates_are_stopped_and_diagnosed() -> None:
    """A recursive template chain cannot loop forever."""
    config = {
        "decluttering_templates": {
            "first": {"card": _decluttering_card("second")},
            "second": {"card": _decluttering_card("first")},
        },
        "views": [
            {"title": "Home", "cards": [_decluttering_card("first")]}
        ],
    }

    result = parse_dashboard(config)

    assert result.entities == {}
    assert [diagnostic.code for diagnostic in result.diagnostics] == [
        "circular_template"
    ]
    assert "first -> second -> first" in result.diagnostics[0].message


def test_template_depth_limit_stops_pathological_nesting() -> None:
    """Unique templates cannot bypass the maximum recursion depth."""
    templates = {
        f"level_{index}": {
            "card": _decluttering_card(f"level_{index + 1}")
        }
        for index in range(20)
    }
    templates["level_20"] = {"card": {"entity": "sensor.too_deep"}}
    config = {
        "decluttering_templates": templates,
        "views": [
            {"title": "Home", "cards": [_decluttering_card("level_0")]}
        ],
    }

    result = parse_dashboard(config)

    assert result.entities == {}
    assert [diagnostic.code for diagnostic in result.diagnostics] == [
        "max_template_depth"
    ]


def test_button_card_triple_brackets_are_not_decluttering_placeholders() -> None:
    """Button-Card JavaScript syntax must survive template substitution."""
    config = {
        "decluttering_templates": {
            "javascript_tile": {
                "card": {
                    "type": "custom:button-card",
                    "entity": "[[entity]]",
                    "label": (
                        "[[[ return states['sensor.javascript_reference'].state "
                        "+ states['switch.[[entity]]']?.state; ]]]"
                    ),
                }
            }
        },
        "views": [
            {
                "title": "Home",
                "cards": [
                    _decluttering_card(
                        "javascript_tile", [{"entity": "sensor.direct_reference"}]
                    )
                ],
            }
        ],
    }

    result = parse_dashboard(config)

    assert result.entities == {
        "sensor.direct_reference": ["Home"],
        "sensor.javascript_reference": ["Home"],
    }
    assert result.diagnostics == ()
