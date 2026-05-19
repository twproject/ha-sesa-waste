from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, CONF_COMUNE_NAME, CONF_VIA_NAME, DOMAIN
from .coordinator import SesaWasteDataUpdateCoordinator


def _entry_value(entry: ConfigEntry, key: str):
    return entry.options.get(key, entry.data.get(key))


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    coordinator: SesaWasteDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            SesaTodayWasteSensor(coordinator, entry),
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
            "name": "SESA Raccolta Rifiuti",
            "manufacturer": "SESA",
            "configuration_url": "https://app.sesaeste.it",
        }

    @property
    def common_attributes(self):
        return {
            "comune": _entry_value(self.entry, CONF_COMUNE_NAME),
            "via": _entry_value(self.entry, CONF_VIA_NAME),
        }


class SesaTodayWasteSensor(BaseSesaSensor):
    _attr_name = "Raccolta oggi"
    _attr_icon = "mdi:calendar-today"
    _attr_device_class = SensorDeviceClass.ENUM

    def __init__(self, coordinator: SesaWasteDataUpdateCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_today_waste"

    @property
    def native_value(self):
        event = self.coordinator.today_event
        return ", ".join(event.types) if event else "Nessuna raccolta"

    @property
    def extra_state_attributes(self):
        event = self.coordinator.today_event
        attrs = self.common_attributes
        attrs.update({
            "date": event.date.isoformat() if event else None,
            "types": event.types if event else [],
            "upcoming": [
                {"date": item.date.isoformat(), "types": item.types}
                for item in (self.coordinator.data or [])[:14]
            ],
        })
        return attrs


class SesaTomorrowWasteSensor(BaseSesaSensor):
    _attr_name = "Raccolta domani"
    _attr_icon = "mdi:calendar-end"
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
        attrs = self.common_attributes
        attrs.update({
            "date": event.date.isoformat() if event else None,
            "types": event.types if event else [],
        })
        return attrs
