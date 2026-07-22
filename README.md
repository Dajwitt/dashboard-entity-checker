# Dashboard Entity Checker

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://www.hacs.xyz/docs/faq/custom_repositories/)
[![Validate](https://github.com/Dajwitt/dashboard-entity-checker/actions/workflows/validate.yml/badge.svg)](https://github.com/Dajwitt/dashboard-entity-checker/actions/workflows/validate.yml)
[![Tests](https://github.com/Dajwitt/dashboard-entity-checker/actions/workflows/tests.yml/badge.svg)](https://github.com/Dajwitt/dashboard-entity-checker/actions/workflows/tests.yml)

Dashboard Entity Checker is a local Home Assistant custom integration that checks selected Lovelace dashboards for entity references that no longer exist.

It loads dashboard configuration through Home Assistant's Python interfaces. It does **not** read or modify `.storage` files and it never changes dashboard cards or entity IDs.

## Why this integration exists

This project started with heavily customized Lovelace dashboards built from deeply nested cards, Decluttering Card templates and Button-Card JavaScript. Missing entity references can be hidden several template levels away from the visible card.

General-purpose Home Assistant maintenance tools such as [Spook](https://spook.boo/) can already detect many problems in conventional dashboards. In deeply nested custom dashboards, however, template indirection and JavaScript references may prevent those tools from seeing the original entity reference. Dashboard Entity Checker complements them by resolving the dashboard structures it supports before checking each resulting entity ID.

It is therefore primarily useful for:

- complex custom dashboards where missing references are hidden inside nested templates or supported JavaScript;
- users who already use Spook but need an additional dashboard-specific check for structures Spook does not resolve;
- users who do not have Spook installed and want a focused dashboard reference checker.

The dashboard selector is intentional: you can scan only the custom or problem-prone dashboards that need this deeper analysis, or select several dashboards when you want broader coverage. This integration is not affiliated with Spook and does not replace Spook's wider Home Assistant repair and maintenance checks.

> [!IMPORTANT]
> This project is currently a pre-1.0 public release and is not yet included in the default HACS catalog. Install it as a **custom HACS repository** using the instructions below.

## What counts as missing?

An entity is reported only when it exists in neither:

- Home Assistant's current state machine, nor
- Home Assistant's entity registry.

Entities that are unavailable, disabled, or currently have no state are therefore not reported as missing when a registry entry still exists.

## Features

- Select and scan one or more Lovelace dashboards
- Group one missing entity across all affected dashboards and views
- Detect direct entity references in dashboard configuration
- Detect relevant Button-Card JavaScript references, including JavaScript comments
- Resolve nested Decluttering Card templates, defaults, variables and complete card objects
- Filter service calls, URLs, CSS, icons, card types and unsupported dynamic JavaScript fragments
- Keep template-resolution diagnostics separate from missing-entity alerts
- Ignore configured exact entity IDs while retaining transparent `ignored_matches`
- Scan automatically after Home Assistant has fully started and then at the configured interval
- Trigger an immediate scan with `dashboard_entity_checker.scan_now`
- Serialize scheduled and manual scans to prevent overlapping work
- Report results through `sensor.dashboard_entity_checker`
- Maintain one persistent notification, update it only when needed, and remove it after a clean scan
- Retain successful dashboard results when another selected dashboard cannot be loaded
- Fire `dashboard_entity_checker_result_changed` after a complete result changes
- Provide redacted Home Assistant diagnostics
- English and German interface text

## Installation

### HACS custom repository

HACS must already be installed and working.

[![Open your Home Assistant instance and add this repository to HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Dajwitt&repository=dashboard-entity-checker&category=integration)

If the button is not available in your environment:

1. Open **HACS** in Home Assistant.
2. Open the three-dot menu in the top-right corner.
3. Select **Custom repositories**.
4. Enter this repository URL:

   ```text
   https://github.com/Dajwitt/dashboard-entity-checker
   ```

5. Select the category **Integration** and add the repository.
6. Open **Dashboard Entity Checker** in HACS and choose **Download**.
7. Restart Home Assistant.
8. Continue with the configuration steps below.

Do not add anything to `configuration.yaml`.

### Manual installation

1. Download the latest release from GitHub.
2. Copy `custom_components/dashboard_entity_checker` to:

   ```text
   /config/custom_components/dashboard_entity_checker
   ```

3. Restart Home Assistant.
4. Continue with the configuration steps below.

## Configuration

After installation and restart:

1. Open **Settings → Devices & services**.
2. Select **Add integration**.
3. Search for **Dashboard Entity Checker**.
4. Select one or more dashboards.
5. Set the scan interval in minutes. The default is 5 minutes.
6. Enable or disable persistent notifications.
7. Optionally enter exact entity IDs to ignore, one per line.

Configuration and later changes are handled through Home Assistant's Config Flow and Options Flow. No YAML configuration is required.

## Result sensor

The integration creates `sensor.dashboard_entity_checker`.

- **State:** number of currently missing, non-ignored entities
- **`missing_entities`:** missing IDs with dashboard and view locations
- **`ignored_entities`:** configured exact ignore list
- **`ignored_matches`:** missing references suppressed by the ignore list
- **`dashboards_loaded`:** dashboards loaded successfully during the latest scan
- **`dashboard_errors`:** selected dashboards that could not be loaded
- **`template_diagnostics`:** non-fatal Decluttering resolution diagnostics
- **`last_scan`:** time of the latest completed scan
- **`last_error`:** understandable summary of a dashboard loading problem

A partial dashboard failure is not treated as a clean all-dashboard result. Successfully loaded dashboards remain available in the sensor attributes, while the failed dashboard is listed under `dashboard_errors`.

## Immediate scan

Use this action in Developer Tools, scripts or automations:

```yaml
action: dashboard_entity_checker.scan_now
```

## Result-changed event

After the first complete scan establishes a baseline, a changed complete result fires:

```text
dashboard_entity_checker_result_changed
```

The event data contains:

- selected dashboards
- previous and current missing counts
- added and removed entity IDs
- the complete current missing-entity result with locations
- scan time

Unchanged scans and partial dashboard failures do not fire this event.

## Persistent notification behavior

When notifications are enabled:

- one fixed persistent notification is used;
- repeated identical results do not create duplicates;
- changed locations update the existing notification;
- a complete clean scan removes the notification;
- disabling notifications also removes it.

## Diagnostics

Download diagnostics from the integration menu under **Settings → Devices & services** when reporting a problem. Diagnostics include selected and successfully loaded dashboards, structured loading errors, scan counts, missing references, ignored matches and template diagnostics. Token-, password- and access-token-like fields are redacted.

## Known limits

- JavaScript is analyzed as text; it is not executed.
- Fully dynamic entity IDs such as template-literal fragments cannot be resolved safely and are ignored.
- Only references present in dashboard configuration or supported template expansion can be checked.
- Decluttering variables that cannot be resolved are reported as template diagnostics rather than guessed.
- JavaScript comments are intentionally scanned because stale entity references are often left there.
- The integration reports problems but does not edit dashboards or offer automatic repairs.

## Requirements

- Home Assistant 2026.7.0 or newer
- HACS 2.0.0 or newer for HACS installation

## Support

Before opening an issue:

1. Confirm that the latest release is installed.
2. Run an immediate scan.
3. Check `dashboard_errors`, `last_error` and `template_diagnostics`.
4. Download the integration diagnostics.
5. Open an issue at <https://github.com/Dajwitt/dashboard-entity-checker/issues> with the diagnostics and clear reproduction steps.

Do not post access tokens, passwords or private Home Assistant URLs.

## Release status

- **v0.3.1:** ignore list can be cleared completely
- **v0.3.0:** multiple dashboards, nested Decluttering resolution, ignore list and result-change events
- **Next milestone:** v1.0 release hardening, documented limits and default HACS catalog submission readiness
