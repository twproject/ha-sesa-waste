from __future__ import annotations

from datetime import date, timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import SesaClient, WasteEvent
from .const import (
    CONF_COMUNE_ID,
    CONF_NOTIFICHE,
    CONF_VIA_ID,
    DEFAULT_BASE_URL,
    DOMAIN,
    UPDATE_INTERVAL_HOURS,
)

_LOGGER = logging.getLogger(__name__)


class SesaWasteDataUpdateCoordinator(DataUpdateCoordinator[list[WasteEvent]]):
    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.entry = entry
        self.client = SesaClient(
            base_url=entry.data.get("base_url", DEFAULT_BASE_URL),
            comune_id=entry.data[CONF_COMUNE_ID],
            via_id=entry.data[CONF_VIA_ID],
            notifiche=entry.data.get(CONF_NOTIFICHE, False),
            session_id=entry.data.get("session_id"),
            device_uuid=entry.data.get("device_uuid"),
        )

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=UPDATE_INTERVAL_HOURS),
        )

    async def _async_update_data(self) -> list[WasteEvent]:
        try:
            return await self.hass.async_add_executor_job(self._sync_update)
        except Exception as exc:
            raise UpdateFailed(str(exc)) from exc

    def _sync_update(self) -> list[WasteEvent]:
        self.client.ensure_configured()
        start = date.today()
        end = date(start.year, 12, 31)
        return self.client.get_calendar(start, end)

    def events_between(self, start: date, end: date) -> list[WasteEvent]:
        return [
            event for event in (self.data or [])
            if start <= event.date <= end
        ]

    @property
    def next_event(self) -> WasteEvent | None:
        today = date.today()
        future = [event for event in (self.data or []) if event.date >= today]
        return min(future, key=lambda item: item.date, default=None)

    @property
    def tomorrow_event(self) -> WasteEvent | None:
        tomorrow = date.today() + timedelta(days=1)
        for event in self.data or []:
            if event.date == tomorrow:
                return event
        return None
