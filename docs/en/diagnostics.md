# Diagnostics

Diagnostics are generated under **Settings → Devices & services → Dashboard Entity Checker → three-dot menu → Download diagnostics**. They contain configuration and the latest scan result in a format intended for issue reports.

## Included data

- integration version
- configured, loaded, and failed dashboards
- scan interval and loading state
- views and number of checked references
- active findings, configured exclusions, and `ignored_matches`
- resolved Decluttering templates and template diagnostics
- timestamp and error text from the latest scan

If the coordinator is unavailable when diagnostics are downloaded, the integration returns a reduced data set containing configuration values, empty result lists, and the message `Coordinator ist nicht verfügbar.`

## Example excerpt

```json
{
  "integration_version": "0.3.6",
  "dashboards": ["example-main", "example-tablet"],
  "dashboards_loaded": ["example-main"],
  "dashboard_errors": [
    {"dashboard": "example-tablet", "error": "Dashboard could not be loaded"}
  ],
  "entities_checked": 42,
  "missing_entities": [
    {
      "entity": "sensor.example_retired_temperature",
      "locations": [
        {"dashboard": "example-main", "views": ["Climate"]}
      ]
    }
  ],
  "template_diagnostics": []
}
```

## Redaction

Fields named `access_token`, `token`, and `password` are redacted through Home Assistant's diagnostics helper. This is an additional safeguard and does not replace manual review.

## Before uploading

- Read the complete file.
- Anonymize private dashboard names, view titles, and entity IDs when needed.
- Never publish tokens, passwords, private URLs, or internal network addresses.
- Include the integration version, Home Assistant version, and clear reproduction steps in the issue.
