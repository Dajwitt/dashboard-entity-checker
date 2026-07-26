# Configuration

Initial setup and later changes use Home Assistant's config flow and options flow. No YAML configuration is required.

## Initial setup

After installation and restart:

1. Open **Settings → Devices & services**.
2. Select **Add integration**.
3. Search for **Dashboard Entity Checker**.
4. Select at least one dashboard.
5. Set the scan interval between 1 and 1440 minutes; the default is 5 minutes.
6. Enable or disable persistent notifications.
7. Optionally search all Home Assistant entities and select or enter exact entity IDs to ignore.

Setup is rejected if no dashboard is selected, a selected dashboard cannot be loaded, or an ignored ID is syntactically invalid.

## Configuration fields

| Field | Type | Default | Meaning |
|---|---|---|---|
| Dashboards | Multiple selection | `my-ha-dashboard` | Lovelace dashboards to scan |
| Scan interval | Integer 1–1440 | 5 minutes | Time between automatic scans |
| Notifications | On/off | On | Persistent notification for active findings |
| Ignored entity IDs | Searchable multiple selection | empty | Search all existing and registered entities or enter exact IDs freely |

`my-ha-dashboard` is only the integration's technical default. The selector lists dashboards available on the current Home Assistant instance.

The entity selector combines the current state machine with the complete entity registry. It therefore also offers registered, disabled, unavailable, or currently stateless entities. Current checker findings and already saved ignore IDs remain visible; completely deleted IDs can be entered as a custom exact value.

## Changing options

Open **Settings → Devices & services → Dashboard Entity Checker → Configure**. Every field can be changed there. Saving reloads the config entry; the next scan immediately uses the new values.

Disabling notifications removes the integration's existing persistent notification. The sensor and event remain active.

## Single instance

Exactly one config entry is allowed per Home Assistant instance. That single entry can scan multiple dashboards.

## Migrating older configuration

Version 1 config entries with one dashboard are automatically migrated to the version 2 multiple selection. The previously selected dashboard is retained.
