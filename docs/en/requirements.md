# Requirements

## Supported versions

| Component | Minimum version |
|---|---|
| Home Assistant | 2026.7.0 |
| HACS for HACS installation | 2.0.0 |

Version 0.3.6 is a stable pre-1.0 release. Interfaces and attributes are intended to remain stable but can still change before version 1.0.

## Technical classification

| Property | Value |
|---|---|
| Integration type | `service` |
| IoT class | `local_polling` |
| Config flow | yes, version 2 |
| Config entries | one per Home Assistant instance |
| Dependencies | `lovelace`, `persistent_notification` |
| Platform | `sensor` |
| Configuration | UI, no YAML required |

## Supported languages

Config flow, options flow, and notification messages are available in German and English. Internal sensor status values such as `Fehler gefunden` currently remain German regardless of UI language.

## Network and cloud

Scanning runs locally in Home Assistant. The integration itself requires no cloud connection for checking and sends no dashboard content to an external service. HACS or a manual browser download naturally requires GitHub access to install files.

## Release history

| Version | Focus |
|---|---|
| 0.3.6 | native options and search across all Home Assistant entities |
| 0.3.5 | complete detection of accidentally appended dot suffixes |
| 0.3.4 | expanded tests, coverage threshold, and Ruff checks |
| 0.3.3 | project and integration icon |
| 0.3.2 | compact grouped German and English notifications |
| 0.3.1 | ignore list can be cleared completely |
| 0.3.0 | multiple dashboards, nested Decluttering resolution, and result-changed event |

## Project status

The repository is public but is not yet in the default HACS catalog. Until then, install it as a HACS custom repository or manually. Any future v1.0 or default-catalog date is not a firm commitment.
