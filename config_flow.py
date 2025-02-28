import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_USERNAME, CONF_PASSWORD, CONF_NAME
from .const import DOMAIN, CONF_SCAN_INTERVAL, SCAN_INTERVAL_OPTIONS

# Initial configuration schema including the "Switch has PoE" option
DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_NAME): str,
    vol.Required(CONF_HOST): str,
    vol.Required(CONF_USERNAME): str,
    vol.Required(CONF_PASSWORD): str,
    vol.Optional("Switch has PoE", default=True): bool,
    vol.Optional(CONF_SCAN_INTERVAL, default=30): vol.In(SCAN_INTERVAL_OPTIONS),
})

class PoeSwitchConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Cheap Chinese Switches."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)
        return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA)

    @staticmethod
    def async_get_options_flow(config_entry):
        return PoeSwitchOptionsFlow(config_entry)

class PoeSwitchOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Cheap Chinese Switches without allowing to change the PoE option."""
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options. 'Switch has PoE' is not configurable after initial setup."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        options_schema = vol.Schema({
            vol.Required(CONF_HOST, default=self.config_entry.data.get(CONF_HOST)): str,
            vol.Required(CONF_USERNAME, default=self.config_entry.data.get(CONF_USERNAME)): str,
            vol.Required(CONF_PASSWORD, default=self.config_entry.data.get(CONF_PASSWORD)): str,
            vol.Required(CONF_SCAN_INTERVAL, default=self.config_entry.options.get(CONF_SCAN_INTERVAL, 30)): vol.In(SCAN_INTERVAL_OPTIONS)
        })
        return self.async_show_form(step_id="init", data_schema=options_schema)
