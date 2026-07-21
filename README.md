# Dashboard Entity Checker

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

Home Assistant integration that scans your Lovelace dashboards for **ghost entities** — entity IDs referenced in dashboard YAML that no longer exist in Home Assistant.

## Features

- Scans any Lovelace dashboard for entity references
- Detects missing/deleted entities (ghosts)
- Filters out service calls that look like entity IDs
- Reports results via Home Assistant services

## Installation

### HACS (recommended)

1. Add this repository as a custom repository in HACS
2. Search for "Dashboard Entity Checker" in HACS
3. Install and restart Home Assistant

### Manual

Copy the `custom_components/dashboard_entity_checker` folder to your Home Assistant `custom_components` directory.

## Usage

After installation, the integration provides a `dashboard_entity_checker.check_dashboard` service:

```yaml
service: dashboard_entity_checker.check_dashboard
data:
  dashboard_url_path: "my-ha-dashboard"
```

## How It Works

1. Reads the Lovelace dashboard configuration from `.storage`
2. Extracts all entity ID references (e.g. `sensor.temperature`, `light.kitchen`)
3. Filters out known service call patterns (e.g. `light.turn_on`, `script.toggle`)
4. Checks each entity against Home Assistant's entity registry
5. Reports any entities that don't exist

## Requirements

- Home Assistant 2024.1.0 or newer
- HACS 1.34.0 or newer (for HACS installation)
