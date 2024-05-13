"""Adds config flow for TESmart integration."""
from __future__ import annotations
from typing import TypedDict

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME, CONF_IP_ADDRESS, CONF_PORT
from homeassistant.helpers import selector

from .api import (
    TesmartApiClient,
    TesmartApiClientCommunicationError,
    TesmartApiClientError,
)
from .const import DOMAIN, LOGGER

class TesmartConfigInput(TypedDict):
    """Configuration input structure."""

    CONF_NAME: str
    CONF_IP_ADDRESS: str
    CONF_PORT: int | None

CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(
            CONF_NAME,
        ): selector.TextSelector(
            selector.TextSelectorConfig(
                type=selector.TextSelectorType.TEXT
            )
        ),
        vol.Required(
            CONF_IP_ADDRESS,
        ): selector.TextSelector(
            selector.TextSelectorConfig(
                type=selector.TextSelectorType.TEXT
            )
        ),
        vol.Optional(
            CONF_PORT,
        ): selector.TextSelector(
            selector.TextSelectorConfig(
                type=selector.TextSelectorType.NUMBER
            )
        )
    }
)

class TesmartConfigFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for TESmart integration."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: TesmartConfigInput | None = None,
    ) -> config_entries.FlowResult:
        """Handle a flow initialized by the user."""
        errors: dict[str, str] = {}
        config_input: TesmartConfigInput = user_input or {}

        name: str = config_input.get(CONF_NAME, "")
        ip_address: str = config_input.get(CONF_IP_ADDRESS, "")
        port: int | None = config_input.get(CONF_PORT, None)

        if user_input is not None:
            try:
                await self._test_connection(
                    name = user_input[CONF_NAME],
                    ip_address = user_input[CONF_IP_ADDRESS],
                    port = user_input.get(CONF_PORT, None),
                )
            except TesmartApiClientCommunicationError as exception:
                LOGGER.error(exception)
                errors["base"] = "connection"
            except TesmartApiClientError as exception:
                LOGGER.exception(exception)
                errors["base"] = "unknown"

            if not errors:
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(
                CONFIG_SCHEMA,
                suggested_values={
                    CONF_NAME: name,
                    CONF_IP_ADDRESS: ip_address,
                    CONF_PORT: port
                }
            ),
            errors = errors,
        )

    async def _test_connection(self, name: str, ip_address: str, port: int | None) -> bool:
        """Validate device connection details."""
        client = TesmartApiClient(
            name = name,
            ip_address = ip_address,
            port = port
        )
        return await self.hass.async_add_executor_job(
            self._api_connect, client
        )

    def _api_connect(self, client: TesmartApiClient) -> bool:
        # Synchronous call; wrap in `hass.async_add_executor_job`
        client.refresh_state()
        return client.is_connected
