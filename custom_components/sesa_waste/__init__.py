from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall

from .const import DOMAIN, SERVICE_AGGIORNA_CALENDARIO
from .coordinator import SesaWasteDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.CALENDAR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator = SesaWasteDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    _async_register_services(hass)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


def _async_register_services(hass: HomeAssistant) -> None:
    if hass.services.has_service(DOMAIN, SERVICE_AGGIORNA_CALENDARIO):
        return

    async def async_handle_refresh(call: ServiceCall) -> None:
        _LOGGER.info("Aggiornamento manuale calendario SESA richiesto")
        coordinators: dict[str, SesaWasteDataUpdateCoordinator] = hass.data.get(DOMAIN, {})
        for coordinator in coordinators.values():
            await coordinator.async_request_refresh()

    hass.services.async_register(
        DOMAIN,
        SERVICE_AGGIORNA_CALENDARIO,
        async_handle_refresh,
    )


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

    if unload_ok and not hass.data.get(DOMAIN):
        hass.services.async_remove(DOMAIN, SERVICE_AGGIORNA_CALENDARIO)

    return unload_ok
