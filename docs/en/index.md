# Dashboard Entity Checker

**Documentation for preview version 0.3.6b2** · Home Assistant custom integration

Dashboard Entity Checker scans selected Lovelace dashboards for entity references that exist in neither Home Assistant's state machine nor its entity registry.

The integration reads dashboard configuration through Home Assistant's Python interfaces. It does not read or modify `.storage` files, execute JavaScript, or repair cards or entity IDs.

## Why use this integration?

In complex custom dashboards, missing references can be hidden inside nested cards, Decluttering Card templates, or Button-Card JavaScript. Dashboard Entity Checker resolves the structures it explicitly supports and complements general maintenance tools such as [Spook](https://spook.boo/). It does not replace their wider Home Assistant checks and is not affiliated with Spook.

## Main features

- scan one or more selected dashboards
- collect direct entity IDs, supported Button-Card JavaScript references, and nested Decluttering templates
- report complete locations by dashboard and view
- transparently exclude intentionally missing exact entity IDs
- provide a result sensor, an optional persistent notification, and a change event
- expose partial dashboard failures without discarding valid results from other dashboards
- provide redacted diagnostics for issue reports

## Quick start

1. [Install the integration](./installation.md).
2. [Configure dashboards and scan options](./configuration.md).
3. Inspect `sensor.dashboard_entity_checker` under [Result sensor](./sensor.md).
4. Run `dashboard_entity_checker.scan_now` when an immediate scan is needed.

The following topics cover setup, features, and troubleshooting. For a new installation, start with Installation, Configuration, and How it works.

## Documentation

## Security and privacy

Processing takes place locally in Home Assistant. Before publishing diagnostics, still review private dashboard names, URLs, and other sensitive details. Credentials must never be posted in issues or forum topics.
