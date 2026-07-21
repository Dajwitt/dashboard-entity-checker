"""Constants for Dashboard Entity Checker."""

DOMAIN = "dashboard_entity_checker"
NAME = "Dashboard Entity Checker"
VERSION = "0.1.5"

CONF_DASHBOARD = "dashboard_url_path"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_NOTIFICATIONS = "notifications"

DEFAULT_DASHBOARD = "my-ha-dashboard"
DEFAULT_SCAN_INTERVAL = 5  # minutes
DEFAULT_NOTIFICATIONS = True

NOTIFICATION_ID = "dashboard_entity_checker_missing_entities"

# Entity domains to scan for in dashboard configs
ENTITY_DOMAINS = [
    "alarm_control_panel", "automation", "binary_sensor", "button", "calendar",
    "camera", "climate", "cover", "device_tracker", "fan", "group", "humidifier",
    "input_boolean", "input_button", "input_datetime", "input_number",
    "input_select", "input_text", "light", "lock", "media_player", "number",
    "person", "remote", "scene", "script", "select", "sensor", "switch",
    "timer", "update", "vacuum", "weather", "zone",
]
