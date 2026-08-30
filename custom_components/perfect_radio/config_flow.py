"""Config flow for Perfect Radio."""

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN


class PerfectRadioConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Perfect Radio."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict | None = None
    ) -> FlowResult:
        """Handle the initial setup step."""

        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            return self.async_create_entry(
                title="Perfect Radio",
                data={},
            )

        return self.async_show_form(
            step_id="user",
        )
