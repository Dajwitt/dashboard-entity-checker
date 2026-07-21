"""Config flow for Dashboard Entity Checker."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import (
    CONF_DASHBOARD,
    CONF_DASHBOARDS,
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

    VERSION = 2

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        errors: dict[str, str] = {}
        if user_input is not None:
            errors = await _validate_dashboard_selection(self.hass, user_input)
            if not errors:
                return self.async_create_entry(title=NAME, data=user_input)

        dashboards = await _get_dashboards(self.hass)
        selected = (
            _selected_dashboard_urls(user_input)
            if user_input is not None
            else [DEFAULT_DASHBOARD]
        )
        _include_unavailable_selections(dashboards, selected)

        return self.async_show_form(
            step_id="user",
            data_schema=_dashboard_schema(
                dashboards,
                selected,
                DEFAULT_SCAN_INTERVAL,
                DEFAULT_NOTIFICATIONS,
            ),
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
        current = {**self.config_entry.data, **self.config_entry.options}

        if user_input is not None:
            errors = await _validate_dashboard_selection(self.hass, user_input)
            if not errors:
                return self.async_create_entry(data=user_input)
            current = user_input

        dashboards = await _get_dashboards(self.hass)
        selected = _selected_dashboard_urls(current)
        _include_unavailable_selections(dashboards, selected)

        return self.async_show_form(
            step_id="init",
            data_schema=_dashboard_schema(
                dashboards,
                selected,
                current.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                current.get(CONF_NOTIFICATIONS, DEFAULT_NOTIFICATIONS),
            ),
            errors=errors,
        )


def _dashboard_schema(
    dashboards: dict[str, str],
    selected: list[str],
    scan_interval: int,
    notifications: bool,
) -> vol.Schema:
    """Build the shared config/options schema."""
    options = [
        {"value": url_path, "label": title}
        for url_path, title in dashboards.items()
    ]
    return vol.Schema(
        {
            vol.Required(CONF_DASHBOARDS, default=selected): SelectSelector(
                SelectSelectorConfig(
                    options=options,
                    multiple=True,
                    mode=SelectSelectorMode.LIST,
                )
            ),
            vol.Required(
                CONF_SCAN_INTERVAL, default=scan_interval
            ): vol.All(vol.Coerce(int), vol.Range(min=1, max=1440)),
            vol.Required(CONF_NOTIFICATIONS, default=notifications): bool,
        }
    )


async def _validate_dashboard_selection(
    hass, user_input: dict[str, Any]
) -> dict[str, str]:
    """Ensure at least one selected dashboard can be loaded."""
    selected = _selected_dashboard_urls(user_input)
    if not selected:
        return {CONF_DASHBOARDS: "no_dashboard_selected"}

    for dashboard_url in selected:
        try:
            await load_dashboard(hass, dashboard_url)
        except DashboardError:
            return {CONF_DASHBOARDS: "dashboard_not_found"}
    return {}


def _selected_dashboard_urls(data: dict[str, Any] | None) -> list[str]:
    """Read multi-dashboard selection with legacy scalar fallback."""
    if not data:
        return []
    raw = data.get(CONF_DASHBOARDS)
    if isinstance(raw, (list, tuple)):
        return [item for item in raw if isinstance(item, str) and item]
    legacy = data.get(CONF_DASHBOARD)
    return [legacy] if isinstance(legacy, str) and legacy else []


def _include_unavailable_selections(
    dashboards: dict[str, str], selected: list[str]
) -> None:
    """Keep deleted/temporarily unavailable selections visible in options."""
    for dashboard_url in selected:
        dashboards.setdefault(dashboard_url, dashboard_url)


async def _get_dashboards(hass) -> dict[str, str]:
    """Get available Lovelace dashboards as {url_path: title}."""
    try:
        dashboards = hass.data["lovelace"].dashboards
    except (KeyError, AttributeError):
        return {DEFAULT_DASHBOARD: DEFAULT_DASHBOARD}

    result: dict[str, str] = {}
    for url_path, dashboard in dashboards.items():
        if url_path is None:
            continue
        metadata = dashboard.config or {}
        title = metadata.get("title", url_path)
        if url_path:
            result[url_path] = title

    if not result:
        result[DEFAULT_DASHBOARD] = DEFAULT_DASHBOARD
    return result
