# Dashboard Entity Checker

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![Validate](https://github.com/Dajwitt/dashboard-entity-checker/actions/workflows/validate.yml/badge.svg)](https://github.com/Dajwitt/dashboard-entity-checker/actions/workflows/validate.yml)
[![Tests](https://github.com/Dajwitt/dashboard-entity-checker/actions/workflows/tests.yml/badge.svg)](https://github.com/Dajwitt/dashboard-entity-checker/actions/workflows/tests.yml)

Home Assistant integration that scans your Lovelace dashboards for **ghost entities** — entity IDs referenced in dashboard YAML that no longer exist in Home Assistant.

## Features

- Scans Lovelace dashboards for entity references
- Detects references in Button-Card JavaScript, including comments
- Resolves nested Decluttering Card templates, defaults and variables
- Runs the first scan after Home Assistant startup and repeats it periodically
- Serializes manual and scheduled scans and suppresses unchanged notifications
- Detects missing/deleted entities (ghosts)
- Filters out service calls that look like entity IDs
- Reports results via a sensor entity
- Creates one persistent notification and removes it after a clean scan
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
5. Enable or disable persistent notifications

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

- **v0.1.6** (current): Phase 6 — automatic startup and periodic scans
- **v0.2.0** (planned): diagnostics and configuration extensions
- **v0.3.0** (planned): multiple dashboards, ignore list and result-change events
