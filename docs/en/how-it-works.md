# How it works

## Scan pipeline

```text
Home Assistant fully started
        ↓
load selected dashboards through Lovelace
        ↓
parse views and supported references
        ↓
resolve Decluttering templates and static JavaScript references
        ↓
merge references by dashboard and view
        ↓
check the state machine and entity registry
        ↓
apply the exact ignore list
        ↓
update sensor, adjust notification, optionally fire event
```

## Dashboard access

The integration uses Home Assistant's Lovelace Python interfaces and loads current configuration with a forced refresh. It does not access `.storage` directly and never writes to a dashboard. Only dashboards selected in the config entry are scanned.

## When is an entity missing?

A reference is reported only when it is absent from both places:

- no current state in Home Assistant's state machine
- no entry in the entity registry

Therefore, `unavailable`, disabled, or temporarily stateless entities do not count as missing while a registry entry still exists.

## Locations and deduplication

A missing ID is returned once, with every location retained:

```json
{
  "entity": "sensor.example_retired_temperature",
  "locations": [
    {"dashboard": "example-main", "views": ["Overview", "Climate"]},
    {"dashboard": "example-tablet", "views": ["Details"]}
  ]
}
```

Dashboard values are URL paths; view values are visible titles. Multiple occurrences within the same view do not increase the finding count.

## Automatic and manual scans

The first scan begins only after Home Assistant has fully started. Scans then repeat at the configured interval. `dashboard_entity_checker.scan_now` requests an immediate scan. Manual and scheduled scans are serialized and never overlap.

## Partial failure

If at least one selected dashboard cannot be loaded, results from successfully loaded dashboards are retained. The sensor reports `Teilweise fehlgeschlagen` and exposes details in `dashboard_errors` and `last_error`.

An incomplete scan does not change an existing finding notification and does not fire the result-changed event. This prevents a previous complete result from being replaced by incomplete data. The first subsequent complete scan becomes the new comparison baseline and also does not fire a change event yet.

If none of the selected dashboards can be loaded, the coordinator update fails. The sensor remains available, reports the failed update, and retains the last successful data set while Home Assistant keeps it.
