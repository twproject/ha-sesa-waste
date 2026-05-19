from __future__ import annotations

from datetime import timedelta

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN
from .coordinator import SesaWasteDataUpdateCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    coordinator: SesaWasteDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SesaWasteCalendar(coordinator, entry)])


class SesaWasteCalendar(CoordinatorEntity[SesaWasteDataUpdateCoordinator], CalendarEntity):
    _attr_has_entity_name = True
    _attr_name = "Calendario rifiuti"
    _attr_attribution = ATTRIBUTION
    _attr_icon = "mdi:calendar-month"

    def __init__(self, coordinator: SesaWasteDataUpdateCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_calendar"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "SESA Raccolta Rifiuti",
            "manufacturer": "SESA",
            "configuration_url": "https://app.sesaeste.it",
        }

    @property
    def event(self) -> CalendarEvent | None:
        next_event = self.coordinator.next_event
        if not next_event:
            return None
        return CalendarEvent(
            summary=", ".join(next_event.types),
            start=next_event.date,
            end=next_event.date + timedelta(days=1),
            description="Raccolta rifiuti SESA",
        )

    async def async_get_events(self, hass: HomeAssistant, start_date, end_date):
        events = self.coordinator.events_between(start_date.date(), end_date.date())
        return [
            CalendarEvent(
                summary=", ".join(event.types),
                start=event.date,
                end=event.date + timedelta(days=1),
                description="Raccolta rifiuti SESA",
            )
            for event in events
        ]
