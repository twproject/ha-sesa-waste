from __future__ import annotations

from datetime import date

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN
from .coordinator import SesaWasteDataUpdateCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    coordinator: SesaWasteDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            SesaNextWasteSensor(coordinator, entry),
            SesaTomorrowWasteSensor(coordinator, entry),
        ]
    )


class BaseSesaSensor(CoordinatorEntity[SesaWasteDataUpdateCoordinator], SensorEntity):
    _attr_has_entity_name = True
    _attr_attribution = ATTRIBUTION

    def __init__(self, coordinator: SesaWasteDataUpdateCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self.entry = entry
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "SESA Waste Collection",
            "manufacturer": "SESA",
        }


class SesaNextWasteSensor(BaseSesaSensor):
    _attr_name = "Next Waste"
    _attr_icon = "mdi:trash-can"
    _attr_device_class = SensorDeviceClass.ENUM

    def __init__(self, coordinator: SesaWasteDataUpdateCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_next_waste"

    @property
    def native_value(self):
        event = self.coordinator.next_event
        return ", ".join(event.types) if event else None

    @property
    def extra_state_attributes(self):
        event = self.coordinator.next_event
        return {
            "date": event.date.isoformat() if event else None,
            "types": event.types if event else [],
            "upcoming": [
                {"date": item.date.isoformat(), "types": item.types}
                for item in (self.coordinator.data or [])[:14]
            ],
        }


class SesaTomorrowWasteSensor(BaseSesaSensor):
    _attr_name = "Tomorrow Waste"
    _attr_icon = "mdi:calendar-tomorrow"
    _attr_device_class = SensorDeviceClass.ENUM

    def __init__(self, coordinator: SesaWasteDataUpdateCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_tomorrow_waste"

    @property
    def native_value(self):
        event = self.coordinator.tomorrow_event
        return ", ".join(event.types) if event else "Nessuna raccolta"

    @property
    def extra_state_attributes(self):
        event = self.coordinator.tomorrow_event
        return {
            "date": event.date.isoformat() if event else None,
            "types": event.types if event else [],
        }
