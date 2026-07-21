"""Tests for the pure Phase-2 dashboard parser."""

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


def test_non_entities_and_service_names_are_ignored() -> None:
    """Icons, URLs, CSS, services and embedded JavaScript are not Phase-2 IDs."""
    config = {
        "views": [
            {
                "path": "test",
                "cards": [
                    {"icon": "mdi:weather-sunny"},
                    {"type": "custom:button-card"},
                    {"url": "https://example.org/sensor.fake"},
                    {"style": "linear-gradient(red, blue)"},
                    {"service": "light.turn_on"},
                    {"perform_action": "media_player.media_play"},
                    {"javascript": "return states['sensor.javascript_only'];"},
                    {"entity": "binary_sensor.window"},
                ],
            }
        ]
    }

    result = parse_dashboard(config)

    assert result.entities == {"binary_sensor.window": ["test"]}


def test_invalid_views_are_handled_without_crashing() -> None:
    """Malformed view containers produce an empty, valid result."""
    assert parse_dashboard({"views": "invalid"}).entities == {}
    assert parse_dashboard({}).views == []
