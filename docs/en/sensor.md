# Result sensor

The integration creates a sensor entity. Its default entity ID is `sensor.dashboard_entity_checker`; Home Assistant may assign a different ID after a naming conflict or manual rename.

## State

| Value | Meaning |
|---|---|
| `0` | no currently missing, non-ignored entity IDs |
| positive integer | number of unique active findings |

During a partial dashboard failure, the numeric state still represents successfully loaded dashboards. For a complete assessment, also inspect `status`, `dashboard_loaded`, and `dashboard_errors`.

## Attributes

| Attribute | Type | Meaning |
|---|---|---|
| `dashboard` | string | first configured dashboard, compatibility field |
| `dashboards` | list | all configured dashboard URL paths |
| `dashboards_loaded` | list | dashboards loaded successfully in the latest run |
| `dashboard_errors` | list | dashboards not loaded, with error messages |
| `scan_interval_minutes` | number | configured scan interval |
| `dashboard_loaded` | boolean | `true` when every dashboard loaded |
| `status` | string | summarized run status |
| `missing_entities` | list | active missing IDs with locations |
| `ignored_entities` | list | configured exact ignored IDs |
| `ignored_matches` | list | IDs actually found but ignored |
| `checked_entities` | number | unique references before existence checks |
| `templates_resolved` | number | total resolved Decluttering templates |
| `template_diagnostics` | list | non-fatal resolution problems |
| `views` | object | loaded view titles per dashboard |
| `views_scanned` | number | total scanned views |
| `last_scan` | string | ISO timestamp of the last completed scan |
| `last_error` | string or `null` | latest dashboard or coordinator error |

## Finding example

```json
[
  {
    "entity": "sensor.example_retired_temperature",
    "locations": [
      {"dashboard": "example-main", "views": ["Overview", "Climate"]},
      {"dashboard": "example-tablet", "views": ["Details"]}
    ]
  }
]
```

## Status values

| Status | Meaning |
|---|---|
| `OK` | complete scan without active findings |
| `Fehler gefunden` | complete scan with active findings |
| `Teilweise fehlgeschlagen` | at least one dashboard failed and at least one loaded |
| `Fehler` | latest coordinator update failed completely |
| `Warte auf ersten Scan` | integration loaded, first scan not completed |

These status values currently come from the integration in German regardless of the selected UI language.
