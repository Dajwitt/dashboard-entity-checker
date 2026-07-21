"""Tests for direct and JavaScript dashboard entity parsing."""

from custom_components.dashboard_entity_checker.parser import parse_dashboard


def test_direct_entities_are_grouped_by_view_and_deduplicated() -> None:
    """Direct IDs are found once per view and retain all view locations."""
    config = {
        "views": [
            {
                "title": "Home",
                "cards": [
                    {"entity": "sensor.temperature"},
                    {"entities": ["light.kitchen", "sensor.temperature"]},
                    {"variables": [{"speaker": "media_player.echo_bad"}]},
                ],
            },
            {
                "title": "Details",
                "cards": [{"entity": "sensor.temperature"}],
            },
        ]
    }

    result = parse_dashboard(config)

    assert result.views == ["Home", "Details"]
    assert result.checked_entities == 3
    assert result.entities == {
        "light.kitchen": ["Home"],
        "media_player.echo_bad": ["Home"],
        "sensor.temperature": ["Home", "Details"],
    }


def test_javascript_state_references_are_extracted_and_deduplicated() -> None:
    """Bracket and dot state access can contain several references per block."""
    config = {
        "views": [
            {
                "title": "JavaScript",
                "cards": [
                    {
                        "type": "custom:button-card",
                        "label": """[[[
                            const room = states['sensor.room_temperature'];
                            const window = states[\"binary_sensor.window\"];
                            const light = states.light.kitchen;
                            return `${room.state} ${states['sensor.room_temperature'].state}`;
                        ]]]""",
                    }
                ],
            }
        ]
    }

    assert parse_dashboard(config).entities == {
        "binary_sensor.window": ["JavaScript"],
        "light.kitchen": ["JavaScript"],
        "sensor.room_temperature": ["JavaScript"],
    }


def test_entity_ids_in_javascript_comments_are_reported_for_version_one() -> None:
    """Phase 4 deliberately scans entity-like IDs in JavaScript comments."""
    config = {
        "views": [
            {
                "title": "Comments",
                "cards": [
                    {
                        "label": """[[[
                            // Legacy reference: sensor.old_temperature
                            return 'No state lookup here';
                        ]]]"""
                    }
                ],
            }
        ]
    }

    assert parse_dashboard(config).entities == {
        "sensor.old_temperature": ["Comments"]
    }


def test_services_css_urls_icons_and_card_types_are_ignored() -> None:
    """Entity-shaped text in known non-entity contexts must not be reported."""
    config = {
        "views": [
            {
                "path": "test",
                "cards": [
                    {"icon": "mdi:weather-sunny"},
                    {"type": "custom:button-card"},
                    {"url": "https://example.org/sensor.url_fake"},
                    {"style": ".sensor.css_fake { color: red; }"},
                    {"service": "light.turn_on"},
                    {"perform_action": "media_player.media_play"},
                    {
                        "label": """[[[
                            const service = 'light.turn_on';
                            const action = \"media_player.media_play\";
                            const weather = states['weather.system'];
                            const age = weather.last_updated;
                            const dynamic = [1, 2].map(i => `sensor.pws_station_${i}`);
                            return service + action + age + dynamic;
                        ]]]"""
                    },
                    {"entity": "binary_sensor.window"},
                ],
            }
        ]
    }

    assert parse_dashboard(config).entities == {
        "binary_sensor.window": ["test"],
        "weather.system": ["test"],
    }


def test_plain_non_javascript_text_does_not_create_embedded_references() -> None:
    """Ordinary labels are not treated as executable JavaScript."""
    config = {
        "views": [
            {
                "title": "Text",
                "cards": [
                    {"name": "Documentation for sensor.not_a_reference"},
                    {"entity": "binary_sensor.window"},
                ],
            }
        ]
    }

    assert parse_dashboard(config).entities == {"binary_sensor.window": ["Text"]}


def test_invalid_views_are_handled_without_crashing() -> None:
    """Malformed view containers produce an empty, valid result."""
    assert parse_dashboard({"views": "invalid"}).entities == {}
    assert parse_dashboard({}).views == []
