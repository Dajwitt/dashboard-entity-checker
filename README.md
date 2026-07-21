# Dashboard Entity Checker

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![Validate](https://github.com/Dajwitt/dashboard-entity-checker/actions/workflows/validate.yml/badge.svg)](https://github.com/Dajwitt/dashboard-entity-checker/actions/workflows/validate.yml)
[![Tests](https://github.com/Dajwitt/dashboard-entity-checker/actions/workflows/tests.yml/badge.svg)](https://github.com/Dajwitt/dashboard-entity-checker/actions/workflows/tests.yml)

Home Assistant integration that scans your Lovelace dashboards for **ghost entities** — entity IDs referenced in dashboard YAML that no longer exist in Home Assistant.

## Features

- Scans Lovelace dashboards for entity references
- Detects missing/deleted entities (ghosts)
- Filters out service calls that look like entity IDs
- Reports results via a sensor entity
- Config Flow — no YAML configuration needed

## Installation

### HACS (recommended)

1. Add this repository as a custom repository in HACS
2. Search for "Dashboard Entity Checker" in HACS
3. Install and restart Home Assistant

### Manual

Copy the `custom_components/dashboard_entity_checker` folder to your Home Assistant `custom_components` directory.

## Configuration

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for "Dashboard Entity Checker"
3. Select the dashboard to check (default: `my-ha-dashboard`)
4. Set the scan interval (default: 5 minutes)
5. The notification setting is reserved and has no effect until Phase 3

## Usage

### Sensor

The integration creates a sensor `sensor.dashboard_entity_checker`:

- **State**: Number of missing entities (0 = all good)
- **Attributes**: Detailed results including entity names and views

### Service

```yaml
action: dashboard_entity_checker.scan_now
```

Triggers an immediate scan of the configured dashboard.

## Requirements

- Home Assistant 2026.7.0 or newer
- HACS 2.0.0 or newer (for HACS installation)

## Development Status

- **v0.1.2** (current): Phase 2 — direct entity IDs, view assignment and state/registry existence checks
- **v0.2.0** (planned): Button-Card JavaScript, decluttering templates and diagnostics extensions
- **v0.3.0** (planned): Decluttering template support, multiple dashboards
