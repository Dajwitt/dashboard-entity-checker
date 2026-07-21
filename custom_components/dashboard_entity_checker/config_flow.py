"""Config flow for Dashboard Entity Checker."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.core import callback
from .const import (
    CONF_DASHBOARD,
    CONF_NOTIFICATIONS,
    CONF_SCAN_INTERVAL,
    DEFAULT_DASHBOARD,
    DEFAULT_NOTIFICATIONS,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    NAME,
)
from .dashboard import DashboardError, load_dashboard


class DashboardEntityCheckerConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Dashboard Entity Checker."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate dashboard can be loaded
            dashboard_url = user_input[CONF_DASHBOARD]
            try:
                await load_dashboard(self.hass, dashboard_url)
            except DashboardError:
                errors[CONF_DASHBOARD] = "dashboard_not_found"

            if not errors:
                return self.async_create_entry(title=NAME, data=user_input)

        # List available dashboards
        dashboards = await _get_dashboards(self.hass)

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_DASHBOARD, default=DEFAULT_DASHBOARD
                ): vol.In(dashboards),
                vol.Required(
                    CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=1440)),
                vol.Required(
                    CONF_NOTIFICATIONS, default=DEFAULT_NOTIFICATIONS
                ): bool,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return DashboardEntityCheckerOptionsFlow(config_entry)


class DashboardEntityCheckerOptionsFlow(OptionsFlow):
    """Handle options flow."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            return self.async_create_entry(data=user_input)

        dashboards = await _get_dashboards(self.hass)
        current = {**self.config_entry.data, **self.config_entry.options}

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_DASHBOARD,
                    default=current.get(
                        CONF_DASHBOARD, DEFAULT_DASHBOARD
                    ),
                ): vol.In(dashboards),
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    default=current.get(
                        CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                    ),
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=1440)),
                vol.Required(
                    CONF_NOTIFICATIONS,
                    default=current.get(
                        CONF_NOTIFICATIONS, DEFAULT_NOTIFICATIONS
                    ),
                ): bool,
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
            errors=errors,
        )


async def _get_dashboards(hass) -> dict[str, str]:
    """Get available Lovelace dashboards as {url_path: title} dict."""
    try:
        dashboards = hass.data["lovelace"].dashboards
    except (KeyError, AttributeError):
        return {DEFAULT_DASHBOARD: DEFAULT_DASHBOARD}

    result: dict[str, str] = {}
    for url_path, dashboard in dashboards.items():
        # The default dashboard uses None as its internal key. Version 0.1
        # targets named dashboards only, especially my-ha-dashboard.
        if url_path is None:
            continue
        metadata = dashboard.config or {}
        title = metadata.get("title", url_path)
        if url_path:
            result[url_path] = title

    if not result:
        result[DEFAULT_DASHBOARD] = DEFAULT_DASHBOARD

    return result
