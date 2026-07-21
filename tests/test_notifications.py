"""Tests for persistent notifications."""

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


def test_notification_message_lists_dashboards_and_views() -> None:
    """The notification preserves every dashboard-to-view location."""
    assert _notification_message(MISSING) == (
        "media_player.echo_bad\n"
        "- my-ha-dashboard → Home\n"
        "- my-ha-dashboard → Bad\n\n"
        "sensor.old_temperature\n"
        "- my-ha-dashboard → Wetter\n"
        "- dashboard-test → Home"
    )


def test_missing_entities_create_or_update_one_notification() -> None:
    """A stable notification ID updates instead of creating duplicates."""
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
        _update_notification(hass, ["my-ha-dashboard"], MISSING, True)

    create.assert_called_once_with(
        hass,
        _notification_message(MISSING),
        title="Dashboard-Fehler: my-ha-dashboard",
        notification_id=NOTIFICATION_ID,
    )
    dismiss.assert_not_called()


def test_multiple_dashboards_use_neutral_notification_title() -> None:
    """The body carries locations when more than one dashboard is selected."""
    hass = object()
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

    assert create.call_args.kwargs["title"] == "Dashboard-Fehler"


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
