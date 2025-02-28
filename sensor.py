from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

def normalize_device_name(name: str) -> str:
    """Convert device name to lowercase and replace spaces with underscores."""
    return name.lower().replace(" ", "_")

class POEPortPowerSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, port, device_name, host):
        super().__init__(coordinator)
        self._port = str(port)
        self._device_name = device_name
        self._host = host
        norm_name = normalize_device_name(device_name)
        # Name includes the device name
        self._attr_name = f"{device_name} Port {port} Power"
        self._attr_unique_id = f"{norm_name}_{host}_port_{port}_power"

    @property
    def native_value(self):
        data = self.coordinator.data.get(self._port, {})
        return data.get("power", 0)

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data.get(self._port, {})
        return {
            "voltage": data.get("voltage", 0),
            "current": data.get("current", 0)
        }

    @property
    def unit_of_measurement(self):
        return "W"

    @property
    def device_info(self):
        system_info = self.coordinator.data.get("system_info", {})
        return {
            "identifiers": {(DOMAIN, self._host)},
            "name": self._device_name,
            "manufacturer": "Cheap Chinese",
            "model": system_info.get("model", "PoE Switch"),
            "sw_version": system_info.get("firmware_version"),
            "hw_version": system_info.get("hardware_version"),
        }

class POEPortLinkSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, port, device_name, host):
        super().__init__(coordinator)
        self._port = str(port)
        self._device_name = device_name
        self._host = host
        norm_name = normalize_device_name(device_name)
        self._attr_name = f"{device_name} Port {port} Link"
        self._attr_unique_id = f"{norm_name}_{host}_port_{port}_link"

    @property
    def native_value(self):
        data = self.coordinator.data.get(self._port, {})
        return data.get("link_status", "Unknown")

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data.get(self._port, {})
        attributes = {
            "tx_good": data.get("tx_good", 0),
            "tx_bad": data.get("tx_bad", 0),
            "rx_good": data.get("rx_good", 0),
            "rx_bad": data.get("rx_bad", 0)
        }
        if "link_speed" in data:
            attributes["link_speed"] = data["link_speed"]
        return attributes

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

class POEDeviceIPSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, device_name, host):
        super().__init__(coordinator)
        self._device_name = device_name
        self._host = host
        norm_name = normalize_device_name(device_name)
        self._attr_name = f"{device_name} IP Address"
        self._attr_unique_id = f"{norm_name}_{host}_ip"

    @property
    def native_value(self):
        system_info = self.coordinator.data.get("system_info", {})
        return system_info.get("ip", "unknown")

    @property
    def extra_state_attributes(self):
        system_info = self.coordinator.data.get("system_info", {})
        return {
            "netmask": system_info.get("netmask", "unknown"),
            "gateway": system_info.get("gateway", "unknown")
        }

    @property
    def device_info(self):
        system_info = self.coordinator.data.get("system_info", {})
        norm_name = normalize_device_name(self._device_name)
        return {
            "identifiers": {(DOMAIN, self._host)},
            "name": self._device_name,
            "manufacturer": "Cheap Chinese",
            "model": system_info.get("model", "PoE Switch"),
        }

class POEDeviceMACSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, device_name, host):
        super().__init__(coordinator)
        self._device_name = device_name
        self._host = host
        norm_name = normalize_device_name(device_name)
        self._attr_name = f"{device_name} Device MAC"
        self._attr_unique_id = f"{norm_name}_{host}_mac"

    @property
    def native_value(self):
        system_info = self.coordinator.data.get("system_info", {})
        return system_info.get("mac", "unknown")

    @property
    def extra_state_attributes(self):
        return {}

    @property
    def device_info(self):
        system_info = self.coordinator.data.get("system_info", {})
        norm_name = normalize_device_name(self._device_name)
        return {
            "identifiers": {(DOMAIN, self._host)},
            "name": self._device_name,
            "manufacturer": "Cheap Chinese",
            "model": system_info.get("model", "PoE Switch"),
        }

class POEOverallPowerSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, device_name, host):
        super().__init__(coordinator)
        self._device_name = device_name
        self._host = host
        norm_name = normalize_device_name(device_name)
        self._attr_name = f"{device_name} Overall PoE Power"
        self._attr_unique_id = f"{norm_name}_{host}_overall_power"

    @property
    def native_value(self):
        return self.coordinator.data.get("overall_power", 0)

    @property
    def unit_of_measurement(self):
        return "W"

    @property
    def device_info(self):
        system_info = self.coordinator.data.get("system_info", {})
        norm_name = normalize_device_name(self._device_name)
        return {
            "identifiers": {(DOMAIN, self._host)},
            "name": self._device_name,
            "manufacturer": "Cheap Chinese",
            "model": system_info.get("model", "PoE Switch"),
        }

async def async_setup_entry(hass, entry, async_add_entities):
    conf = hass.data[DOMAIN][entry.entry_id]["config"]
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    device_name = conf.get("name")
    host = conf.get("host")
    has_poe = conf.get("Switch has PoE", True)
    sensors = []
    # If PoE is enabled, add PoE-specific sensors for ports 1-8
    if has_poe:
        for port in range(1, 9):
            sensors.append(POEPortPowerSensor(coordinator, port, device_name, host))
        sensors.append(POEOverallPowerSensor(coordinator, device_name, host))
    # Always add Link sensors for all 9 ports
    for port in range(1, 10):
        sensors.append(POEPortLinkSensor(coordinator, port, device_name, host))
    # Always add network sensors
    sensors.append(POEDeviceIPSensor(coordinator, device_name, host))
    sensors.append(POEDeviceMACSensor(coordinator, device_name, host))
    async_add_entities(sensors, True)
