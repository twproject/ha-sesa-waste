from __future__ import annotations

from datetime import timedelta

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, CONF_REDFOXY_COLORS, CONF_REDFOXY_COMPAT, DOMAIN
from .coordinator import SesaWasteDataUpdateCoordinator

DEFAULT_REDFOXY_COLORS = {
    "umido": "#8B5A2B",
    "secco": "#9E9E9E",
    "carta": "#2196F3",
    "cartone": "#2196F3",
    "vetro": "#00A651",
    "verde": "#4CAF50",
    "plastica lattine": "#FFD600",
    "plastica": "#FFD600",
    "lattine": "#FFD600",
    "ingombranti": "#424242",
    "pannolini": "#88C2EC",
}


def _entry_value(entry: ConfigEntry, key: str, default=None):
    return entry.options.get(key, entry.data.get(key, default))


def _color_for_type(entry: ConfigEntry, waste_type: str) -> str | None:
    custom_colors = _entry_value(entry, CONF_REDFOXY_COLORS, {}) or {}
    if waste_type in custom_colors:
        return custom_colors[waste_type]
    return DEFAULT_REDFOXY_COLORS.get(waste_type.lower().strip())


def _event_description(entry: ConfigEntry, waste_type: str, redfoxy_enabled: bool) -> str:
    if not redfoxy_enabled:
        return "Raccolta rifiuti SESA"
    color = _color_for_type(entry, waste_type)
    if color:
        return f"color: {color}"
    return "Raccolta rifiuti SESA"


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
    def _redfoxy_enabled(self) -> bool:
        return bool(_entry_value(self.entry, CONF_REDFOXY_COMPAT, False))

    @property
    def event(self) -> CalendarEvent | None:
        next_event = self.coordinator.next_event
        if not next_event:
            return None
        waste_type = next_event.types[0] if next_event.types else "Raccolta rifiuti"
        return CalendarEvent(
            summary=waste_type,
            start=next_event.date,
            end=next_event.date + timedelta(days=1),
            description=_event_description(self.entry, waste_type, self._redfoxy_enabled),
        )

    async def async_get_events(self, hass, start_date, end_date):
        events = self.coordinator.events_between(start_date.date(), end_date.date())
        output: list[CalendarEvent] = []
        for event in events:
            for waste_type in event.types:
                output.append(
                    CalendarEvent(
                        summary=waste_type,
                        start=event.date,
                        end=event.date + timedelta(days=1),
                        description=_event_description(
                            self.entry,
                            waste_type,
                            self._redfoxy_enabled,
                        ),
                    )
                )
        return output
