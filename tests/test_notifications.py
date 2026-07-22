"""Tests for persistent notifications."""

from types import SimpleNamespace
from unittest.mock import patch

from custom_components.dashboard_entity_checker.const import NOTIFICATION_ID
from custom_components.dashboard_entity_checker.coordinator import (
    MissingEntity,
    _notification_message,
    _update_notification,
)

MISSING: list[MissingEntity] = [
    {
        "entity": "media_player.echo_bad",
        "locations": [
            {"dashboard": "my-ha-dashboard", "views": ["Home", "Bad"]}
        ],
    },
    {
        "entity": "sensor.old_temperature",
        "locations": [
            {"dashboard": "my-ha-dashboard", "views": ["Wetter"]},
            {"dashboard": "dashboard-test", "views": ["Home"]},
        ],
    },
]


def test_notification_message_groups_entities_by_dashboard_and_view() -> None:
    """Location-first Markdown avoids repeating a location for every entity."""
    assert _notification_message(MISSING, "de") == (
        "**2 fehlende Entities in 4 Ansichten**\n\n"
        "### `dashboard-test`\n\n"
        "**Home** · 1\n"
        "- `sensor.old_temperature`\n\n"
        "### `my-ha-dashboard`\n\n"
        "**Bad** · 1\n"
        "- `media_player.echo_bad`\n\n"
        "**Home** · 1\n"
        "- `media_player.echo_bad`\n\n"
        "**Wetter** · 1\n"
        "- `sensor.old_temperature`\n\n"
        "_Vollständige Liste: Sensorattribut `missing_entities`._"
    )


def test_notification_message_limits_long_view_lists() -> None:
    """Large custom views stay readable while the sensor keeps all details."""
    missing: list[MissingEntity] = [
        {
            "entity": f"sensor.fake_{index:02d}",
            "locations": [
                {"dashboard": "dashboard-handy", "views": ["Lumen Dashboard"]}
            ],
        }
        for index in range(1, 19)
    ]

    message = _notification_message(missing, "de")

    assert "**18 fehlende Entities in 1 Ansicht**" in message
    assert "**Lumen Dashboard** · 18" in message
    assert "`sensor.fake_01`" in message
    assert "`sensor.fake_08`" in message
    assert "`sensor.fake_09`" not in message
    assert "- _+10 weitere_" in message


def test_missing_entities_create_or_update_one_notification() -> None:
    """A stable notification ID updates instead of creating duplicates."""
    hass = SimpleNamespace(config=SimpleNamespace(language="de"))
    with (
        patch(
            "custom_components.dashboard_entity_checker.coordinator."
            "persistent_notification.async_create"
        ) as create,
        patch(
            "custom_components.dashboard_entity_checker.coordinator."
            "persistent_notification.async_dismiss"
        ) as dismiss,
    ):
        _update_notification(hass, ["my-ha-dashboard"], MISSING, True)

    create.assert_called_once_with(
        hass,
        _notification_message(MISSING, "de"),
        title="Dashboard Entity Checker: 2 fehlende Entities",
        notification_id=NOTIFICATION_ID,
    )
    dismiss.assert_not_called()


def test_multiple_dashboards_use_neutral_notification_title() -> None:
    """English installations receive an English count title."""
    hass = SimpleNamespace(config=SimpleNamespace(language="en"))
    with patch(
        "custom_components.dashboard_entity_checker.coordinator."
        "persistent_notification.async_create"
    ) as create:
        _update_notification(
            hass,
            ["my-ha-dashboard", "dashboard-test"],
            MISSING,
            True,
        )

    assert create.call_args.kwargs["title"] == (
        "Dashboard Entity Checker: 2 missing entities"
    )


def test_clean_scan_dismisses_existing_notification() -> None:
    """A clean scan automatically removes the old notification."""
    hass = object()
    with (
        patch(
            "custom_components.dashboard_entity_checker.coordinator."
            "persistent_notification.async_create"
        ) as create,
        patch(
            "custom_components.dashboard_entity_checker.coordinator."
            "persistent_notification.async_dismiss"
        ) as dismiss,
    ):
        _update_notification(hass, ["my-ha-dashboard"], [], True)

    dismiss.assert_called_once_with(hass, NOTIFICATION_ID)
    create.assert_not_called()


def test_disabled_notifications_remove_stale_notification() -> None:
    """Disabling notifications also clears a previously created message."""
    hass = object()
    with patch(
        "custom_components.dashboard_entity_checker.coordinator."
        "persistent_notification.async_dismiss"
    ) as dismiss:
        _update_notification(hass, ["my-ha-dashboard"], MISSING, False)

    dismiss.assert_called_once_with(hass, NOTIFICATION_ID)
