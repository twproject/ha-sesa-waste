from __future__ import annotations

from datetime import date, timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .api import SesaClient, WasteEvent
from .const import (
    BASE_URL,
    CONF_COMUNE_ID,
    CONF_NOTIFICHE,
    CONF_VIA_ID,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


def _entry_value(entry: ConfigEntry, key: str):
    return entry.options.get(key, entry.data.get(key))


class SesaWasteDataUpdateCoordinator(DataUpdateCoordinator[list[WasteEvent]]):
    """Coordinator that downloads the annual calendar.

    No periodic polling is configured on purpose. The calendar is downloaded:
    - when the integration is loaded/reloaded
    - when Home Assistant starts and the integration is set up
    - when the manual service sesa_waste.aggiorna_calendario is called
    """

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.entry = entry
        self.client = SesaClient(
            base_url=BASE_URL,
            comune_id=_entry_value(entry, CONF_COMUNE_ID),
            via_id=_entry_value(entry, CONF_VIA_ID),
            notifiche=_entry_value(entry, CONF_NOTIFICHE) or False,
            device_uuid=entry.data.get("device_uuid"),
        )

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=None,
        )

    def _today(self) -> date:
        return dt_util.now().date()

    def _current_year_range(self) -> tuple[date, date]:
        today = self._today()
        return date(today.year, 1, 1), date(today.year, 12, 31)

    async def _async_update_data(self) -> list[WasteEvent]:
        try:
            return await self.hass.async_add_executor_job(self._sync_update)
        except Exception as exc:
            raise UpdateFailed(str(exc)) from exc

    def _sync_update(self) -> list[WasteEvent]:
        self.client.ensure_configured()
        start, end = self._current_year_range()
        events = self.client.get_calendar(start, end)
        _LOGGER.debug(
            "Ricevuti %s eventi SESA per anno %s. Primi eventi: %s",
            len(events),
            start.year,
            events[:7],
        )
        return events

    def events_between(self, start: date, end: date) -> list[WasteEvent]:
        return [event for event in (self.data or []) if start <= event.date <= end]

    @property
    def today_event(self) -> WasteEvent | None:
        today = self._today()
        matches = [event for event in (self.data or []) if event.date == today]
        if not matches:
            return None
        return self._merge_events(today, matches)

    @property
    def tomorrow_event(self) -> WasteEvent | None:
        tomorrow = self._today() + timedelta(days=1)
        matches = [event for event in (self.data or []) if event.date == tomorrow]
        if not matches:
            return None
        return self._merge_events(tomorrow, matches)

    @property
    def next_event(self) -> WasteEvent | None:
        today = self._today()
        for event in self.data or []:
            if event.date >= today:
                return event
        return None

    @staticmethod
    def _merge_events(day: date, events: list[WasteEvent]) -> WasteEvent:
        merged: list[str] = []
        for event in events:
            for waste_type in event.types:
                if waste_type not in merged:
                    merged.append(waste_type)
        return WasteEvent(day, merged)
