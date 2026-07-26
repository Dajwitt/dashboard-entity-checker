# Troubleshooting

## Sensor remains at `Warte auf ersten Scan`

The first scan starts only after Home Assistant has fully started. This state is normal shortly after a restart. If it persists, run `dashboard_entity_checker.scan_now` under **Developer Tools → Actions** and inspect the Home Assistant logs.

## `dashboard_errors` contains entries

1. Inspect `last_error` and the individual error message.
2. Confirm the dashboard URL path still exists.
3. Open the dashboard in Home Assistant.
4. Open the integration options and remove or reselect an invalid entry.
5. Scan again.

Results from other dashboards remain visible during partial failures, but they are not a complete overall scan.

## `template_diagnostics` contains entries

| Code | Typical cause |
|---|---|
| `missing_template` | name is missing or template was renamed |
| `circular_template` | templates invoke each other recursively |
| `max_template_depth` | chain exceeds 20 levels |
| `unknown_variable` | required variable or default is missing |
| `invalid_variables` | `default` or `variables` has an invalid structure |

The diagnostic identifies the dashboard, view, template, and when possible the variable or detail. Inspect that source configuration; the checker does not modify it.

## Expected missing ID is not reported

- The ID still has an entity-registry entry.
- The ID is listed in `ignored_entities`; a real match appears in `ignored_matches`.
- The affected dashboard is not selected or could not be loaded.
- The reference is generated dynamically or uses an unsupported custom-card format.
- The ID uses an unsupported domain.

See [Supported references](./supported-references.md) and [Known limitations](./limitations.md).

## Clearly malformed value is only partially detected

Install version 0.3.5 or newer. This version handles accidentally appended dot suffixes as the complete malformed scalar. Restart Home Assistant after updating and run a manual scan.

## Entity-like action name is reported

Direct values under the modern dashboard key `action` are not currently excluded like `service` and `perform_action`. For example, `light.example_turn_on` can appear as a missing entity. Inspect the reported location; this behavior is documented under [Known limitations](./limitations.md).

## Notification is absent or unchanged

- Check the notification option.
- Inspect `missing_entities`.
- During a partial failure, the previous notification deliberately remains unchanged.
- An identical complete result causes no unnecessary update.

## Creating an issue report

1. Install the latest version and restart Home Assistant.
2. Run a manual scan.
3. Inspect sensor attributes and Home Assistant logs.
4. Download and redact [Diagnostics](./diagnostics.md).
5. Open an issue under [GitHub Issues](https://github.com/Dajwitt/dashboard-entity-checker/issues) with clear steps and the expected result.

Do not publicly post credentials, private URLs, or real private entity IDs.
