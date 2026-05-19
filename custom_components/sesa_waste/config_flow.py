from __future__ import annotations

import uuid as uuidlib

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .api import SesaClient
from .const import (
    CONF_COMUNE_ID,
    CONF_NOTIFICHE,
    CONF_VIA_ID,
    DEFAULT_BASE_URL,
    DEFAULT_COMUNE_ID,
    DEFAULT_NOTIFICHE,
    DEFAULT_VIA_ID,
    DOMAIN,
)


class SesaWasteConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors: dict[str, str] = {}

        if user_input is not None:
            device_uuid = str(uuidlib.uuid4())
            client = SesaClient(
                base_url=user_input["base_url"],
                comune_id=user_input[CONF_COMUNE_ID],
                via_id=user_input[CONF_VIA_ID],
                notifiche=user_input[CONF_NOTIFICHE],
                device_uuid=device_uuid,
            )

            try:
                await self.hass.async_add_executor_job(client.ensure_configured)
            except Exception:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(
                    f"{user_input[CONF_COMUNE_ID]}-{user_input[CONF_VIA_ID]}"
                )
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"SESA {user_input[CONF_COMUNE_ID]}/{user_input[CONF_VIA_ID]}",
                    data={
                        **user_input,
                        "device_uuid": device_uuid,
                        "session_id": client.session_id,
                    },
                )

        schema = vol.Schema(
            {
                vol.Required("base_url", default=DEFAULT_BASE_URL): str,
                vol.Required(CONF_COMUNE_ID, default=DEFAULT_COMUNE_ID): int,
                vol.Required(CONF_VIA_ID, default=DEFAULT_VIA_ID): int,
                vol.Required(CONF_NOTIFICHE, default=DEFAULT_NOTIFICHE): bool,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return SesaWasteOptionsFlow(config_entry)


class SesaWasteOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({}),
        )
