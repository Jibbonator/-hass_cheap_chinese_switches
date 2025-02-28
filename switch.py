import requests
from hashlib import md5
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
import logging

_LOGGER = logging.getLogger(__name__)

def normalize_device_name(name: str) -> str:
    """Convert device name to lowercase and replace spaces with underscores."""
    return name.lower().replace(" ", "_")

def get_cookie(username, password):
    return md5((username + password).encode('utf-8')).hexdigest()

class POEPortSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(self, coordinator, port, host, username, password, device_name):
        super().__init__(coordinator)
        self._port = port
        self._host = host
        self._username = username
        self._password = password
        self._device_name = device_name
        norm_name = normalize_device_name(device_name)
        # Rename to "Port X PoE" including the device name
        self._attr_name = f"{device_name} Port {port} PoE"
        self._attr_unique_id = f"{norm_name}_{host}_switch_{port}"

    @property
    def is_on(self):
        data = self.coordinator.data.get(str(self._port), {})
        return data.get("status", "Disable") == "Enable"

    @property
    def icon(self):
        return "mdi:power-plug" if self.is_on else "mdi:power-plug-off"

    @property
    def device_info(self):
        system_info = self.coordinator.data.get("system_info", {})
        norm_name = normalize_device_name(self._device_name)
        return {
            "identifiers": {(DOMAIN, self._host)},
            "name": self._device_name,
            "manufacturer": "Cheap Chinese",
            "model": system_info.get("model", "PoE Switch"),
            "sw_version": system_info.get("firmware_version"),
            "hw_version": system_info.get("hardware_version"),
        }

    def _login(self, session):
        session.cookies.set('admin', get_cookie(self._username, self._password))
        return True

    def _set_poe_port(self, state):
        session = requests.Session()
        self._login(session)
        state_value = "1" if state else "0"
        control_url = f"http://{self._host}/pse_port.cgi"
        payload = {
            "portid": self._port - 1,
            "state": state_value,
            "submit": "Apply",
            "cmd": "poe"
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        try:
            response = session.post(control_url, data=payload, headers=headers, timeout=10)
            if response.status_code == 200:
                _LOGGER.info("Port %s successfully set to %s", self._port, "ON" if state else "OFF")
            else:
                _LOGGER.error("Error switching port %s", self._port)
        except Exception as err:
            _LOGGER.error("Error switching port %s: %s", self._port, err)

    async def async_turn_on(self, **kwargs):
        await self.hass.async_add_executor_job(self._set_poe_port, True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        await self.hass.async_add_executor_job(self._set_poe_port, False)
        await self.coordinator.async_request_refresh()

async def async_setup_entry(hass, entry, async_add_entities):
    conf = hass.data[DOMAIN][entry.entry_id]["config"]
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    device_name = conf.get("name")
    host = conf.get("host")
    username = conf.get("username")
    password = conf.get("password")
    switches = []
    # Only create switches for PoE ports (ports 1-8)
    for port in range(1, 9):
        switches.append(POEPortSwitch(coordinator, port, host, username, password, device_name))
    async_add_entities(switches, True)
