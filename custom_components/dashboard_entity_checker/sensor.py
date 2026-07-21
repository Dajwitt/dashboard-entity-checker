"""Sensor platform for Dashboard Entity Checker.

Reads data from the coordinator. Does NOT load dashboards or run checks itself.
"""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, NAME, VERSION
from .coordinator import DashboardEntityCheckerCoordinator

SENSOR_DESCRIPTION = SensorEntityDescription(
    key="dashboard_entity_checker",
    name=NAME,
    icon="mdi:monitor-dashboard",
    has_entity_name=True,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor from a config entry."""
    coordinator: DashboardEntityCheckerCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([DashboardEntityCheckerSensor(coordinator, entry)])


class DashboardEntityCheckerSensor(CoordinatorEntity, SensorEntity):
    """Sensor showing dashboard entity check results."""

    entity_description = SENSOR_DESCRIPTION

    def __init__(
        self,
        coordinator: DashboardEntityCheckerCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": NAME,
            "manufacturer": "Dajwitt",
            "model": "Dashboard Entity Checker",
            "sw_version": VERSION,
        }

    @property
    def native_value(self) -> int:
        """Return the number of missing entities."""
        if self.coordinator.data is None:
            return 0
        return len(self.coordinator.data.get("missing_entities", []))

    @property
    def extra_state_attributes(self) -> dict:
        """Return detailed attributes."""
        if self.coordinator.data is None:
            return {}
        data = self.coordinator.data
        return {
            "dashboard": data.get("dashboard_url"),
            "status": data.get("status", "unknown"),
            "missing_entities": data.get("missing_entities", []),
            "checked_entities": data.get("checked_entities", 0),
            "views_scanned": data.get("views_scanned", 0),
            "last_scan": str(data.get("last_scan", "")),
        }
