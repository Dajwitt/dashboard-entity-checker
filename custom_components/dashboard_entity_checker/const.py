"""Constants for Dashboard Entity Checker."""

DOMAIN = "dashboard_entity_checker"
NAME = "Dashboard Entity Checker"
VERSION = "0.3.3"

CONF_DASHBOARD = "dashboard_url_path"
CONF_DASHBOARDS = "dashboard_url_paths"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_NOTIFICATIONS = "notifications"
CONF_IGNORED_ENTITIES = "ignored_entities"

DEFAULT_DASHBOARD = "my-ha-dashboard"
DEFAULT_SCAN_INTERVAL = 5  # minutes
DEFAULT_NOTIFICATIONS = True
DEFAULT_IGNORED_ENTITIES = ""

NOTIFICATION_ID = "dashboard_entity_checker_missing_entities"
EVENT_RESULT_CHANGED = "dashboard_entity_checker_result_changed"

# Entity domains to scan for in dashboard configs
ENTITY_DOMAINS = [
    "alarm_control_panel", "automation", "binary_sensor", "button", "calendar",
    "camera", "climate", "cover", "device_tracker", "fan", "group", "humidifier",
    "input_boolean", "input_button", "input_datetime", "input_number",
    "input_select", "input_text", "light", "lock", "media_player", "number",
    "person", "remote", "scene", "script", "select", "sensor", "switch",
    "timer", "update", "vacuum", "weather", "zone",
]
