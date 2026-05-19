from __future__ import annotations

import uuid as uuidlib

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .api import SesaClient
from .const import (
    BASE_URL,
    CONF_COMUNE_ID,
    CONF_COMUNE_NAME,
    CONF_NOTIFICHE,
    CONF_VIA_ID,
    CONF_VIA_NAME,
    DEFAULT_NOTIFICHE,
    DOMAIN,
    FIELD_COMUNE,
    FIELD_VIA,
)


class SesaWasteConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 11

    def __init__(self) -> None:
        self._device_uuid = str(uuidlib.uuid4())
        self._comuni: dict[str, str] = {}
        self._addresses: dict[str, str] = {}
        self._comune_id: str | None = None
        self._comune_name: str | None = None
        self._notifiche: bool = DEFAULT_NOTIFICHE

    async def async_step_user(self, user_input=None):
        errors: dict[str, str] = {}

        if not self._comuni:
            client = SesaClient(BASE_URL, device_uuid=self._device_uuid)
            try:
                self._comuni = await self.hass.async_add_executor_job(client.list_municipalities)
                self._device_uuid = client.device_uuid
            except Exception:
                errors["base"] = "cannot_connect"

        if user_input is not None and not errors:
            self._comune_id = str(user_input[FIELD_COMUNE])
            self._comune_name = self._comuni.get(self._comune_id, self._comune_id)
            self._notifiche = DEFAULT_NOTIFICHE

            client = SesaClient(
                BASE_URL,
                comune_id=self._comune_id,
                device_uuid=self._device_uuid,
            )
            try:
                self._addresses = await self.hass.async_add_executor_job(client.list_addresses)
            except Exception:
                errors["base"] = "cannot_connect"
            else:
                if not self._addresses:
                    errors["base"] = "no_addresses"
                else:
                    return await self.async_step_via()

        comune_options = [
            SelectOptionDict(value=value, label=label)
            for value, label in sorted(self._comuni.items(), key=lambda item: item[1])
        ]

        schema = vol.Schema(
            {
                vol.Required(FIELD_COMUNE): SelectSelector(
                    SelectSelectorConfig(
                        options=comune_options,
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                )
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_via(self, user_input=None):
        errors: dict[str, str] = {}

        if user_input is not None:
            via_id = str(user_input[FIELD_VIA])
            via_name = self._addresses.get(via_id, via_id)

            client = SesaClient(
                BASE_URL,
                comune_id=self._comune_id,
                via_id=via_id,
                notifiche=self._notifiche,
                device_uuid=self._device_uuid,
            )

            try:
                await self.hass.async_add_executor_job(client.ensure_configured)
            except Exception:
                errors["base"] = "cannot_connect"
            else:
                self._device_uuid = client.device_uuid
                await self.async_set_unique_id(f"{self._comune_id}-{via_id}")
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"SESA {self._comune_name}",
                    data={
                        CONF_COMUNE_ID: self._comune_id,
                        CONF_COMUNE_NAME: self._comune_name,
                        CONF_VIA_ID: via_id,
                        CONF_VIA_NAME: via_name,
                        CONF_NOTIFICHE: self._notifiche,
                        "device_uuid": self._device_uuid,
                    },
                )

        via_options = [
            SelectOptionDict(value=value, label=label)
            for value, label in sorted(self._addresses.items(), key=lambda item: item[1])
        ]

        schema = vol.Schema(
            {
                vol.Required(FIELD_VIA): SelectSelector(
                    SelectSelectorConfig(
                        options=via_options,
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                )
            }
        )

        return self.async_show_form(
            step_id="via",
            data_schema=schema,
            errors=errors,
            description_placeholders={"comune": self._comune_name or ""},
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return SesaWasteOptionsFlow(config_entry)


class SesaWasteOptionsFlow(config_entries.OptionsFlowWithReload):
    def __init__(self, config_entry):
        self.config_entry = config_entry
        self._device_uuid = config_entry.data.get("device_uuid") or str(uuidlib.uuid4())
        self._comuni: dict[str, str] = {}
        self._addresses: dict[str, str] = {}
        self._comune_id: str | None = None
        self._comune_name: str | None = None

    async def async_step_init(self, user_input=None):
        return await self.async_step_user(user_input)

    async def async_step_user(self, user_input=None):
        errors: dict[str, str] = {}

        if not self._comuni:
            client = SesaClient(BASE_URL, device_uuid=self._device_uuid)
            try:
                self._comuni = await self.hass.async_add_executor_job(client.list_municipalities)
                self._device_uuid = client.device_uuid
            except Exception:
                errors["base"] = "cannot_connect"

        current_comune = self.config_entry.options.get(
            CONF_COMUNE_ID, self.config_entry.data.get(CONF_COMUNE_ID)
        )

        if user_input is not None and not errors:
            self._comune_id = str(user_input[FIELD_COMUNE])
            self._comune_name = self._comuni.get(self._comune_id, self._comune_id)

            client = SesaClient(
                BASE_URL,
                comune_id=self._comune_id,
                device_uuid=self._device_uuid,
            )
            try:
                self._addresses = await self.hass.async_add_executor_job(client.list_addresses)
            except Exception:
                errors["base"] = "cannot_connect"
            else:
                if not self._addresses:
                    errors["base"] = "no_addresses"
                else:
                    return await self.async_step_via()

        comune_options = [
            SelectOptionDict(value=value, label=label)
            for value, label in sorted(self._comuni.items(), key=lambda item: item[1])
        ]

        schema = vol.Schema(
            {
                vol.Required(FIELD_COMUNE, default=current_comune): SelectSelector(
                    SelectSelectorConfig(
                        options=comune_options,
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                )
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_via(self, user_input=None):
        errors: dict[str, str] = {}

        current_via = self.config_entry.options.get(
            CONF_VIA_ID, self.config_entry.data.get(CONF_VIA_ID)
        )

        if user_input is not None:
            via_id = str(user_input[FIELD_VIA])
            via_name = self._addresses.get(via_id, via_id)

            client = SesaClient(
                BASE_URL,
                comune_id=self._comune_id,
                via_id=via_id,
                notifiche=DEFAULT_NOTIFICHE,
                device_uuid=self._device_uuid,
            )

            try:
                await self.hass.async_add_executor_job(client.ensure_configured)
            except Exception:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title="",
                    data={
                        CONF_COMUNE_ID: self._comune_id,
                        CONF_COMUNE_NAME: self._comune_name,
                        CONF_VIA_ID: via_id,
                        CONF_VIA_NAME: via_name,
                        CONF_NOTIFICHE: DEFAULT_NOTIFICHE,
                    },
                )

        via_options = [
            SelectOptionDict(value=value, label=label)
            for value, label in sorted(self._addresses.items(), key=lambda item: item[1])
        ]

        default_via = current_via if current_via in self._addresses else None
        field = vol.Required(FIELD_VIA, default=default_via) if default_via else vol.Required(FIELD_VIA)

        schema = vol.Schema(
            {
                field: SelectSelector(
                    SelectSelectorConfig(
                        options=via_options,
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                )
            }
        )

        return self.async_show_form(
            step_id="via",
            data_schema=schema,
            errors=errors,
            description_placeholders={"comune": self._comune_name or ""},
        )
