# Installation

Dashboard Entity Checker is a custom integration. Version 0.3.6 is the current stable pre-1.0 release and is not yet included in the default HACS catalog.

## Requirements

- Home Assistant 2026.7.0 or newer
- HACS 2.0.0 or newer for HACS installation
- a Lovelace dashboard in storage mode or another dashboard Home Assistant can load through its Lovelace interfaces

## Install with HACS

HACS must already be installed and working.

[Open the custom repository in Home Assistant](https://my.home-assistant.io/redirect/hacs_repository/?owner=Dajwitt&repository=dashboard-entity-checker&category=integration)

If the link does not work:

1. Open HACS in Home Assistant.
2. Open the three-dot menu in the top-right corner.
3. Select **Custom repositories**.
4. Enter this repository URL:

```text
https://github.com/Dajwitt/dashboard-entity-checker
```

5. Select category **Integration** and add the repository.
6. Open **Dashboard Entity Checker** in HACS and select **Download**.
7. Restart Home Assistant.
8. Continue with [Configuration](./configuration.md).

No entry in `configuration.yaml` is required.

## Manual installation

1. Download the latest GitHub release.
2. Ensure the final path looks exactly like this:

```text
/config/custom_components/dashboard_entity_checker/manifest.json
```

3. Copy `custom_components/dashboard_entity_checker` into `/config/custom_components/`.
4. Restart Home Assistant.
5. Continue with [Configuration](./configuration.md).

## Updating

For HACS installations, download the update through HACS and then restart Home Assistant. For manual installations, replace the complete integration directory with the directory from the new release and restart as well.

Creating a Home Assistant backup before updating is recommended. The existing config entry is retained across updates.

## Uninstalling

1. Remove the integration under **Settings → Devices & services**.
2. For a HACS installation, remove the repository through HACS; for a manual installation, delete the `dashboard_entity_checker` directory.
3. Restart Home Assistant.

Removing the integration does not modify any dashboards.
