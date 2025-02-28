import logging
from datetime import timedelta
import requests
import re
from hashlib import md5

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.core import HomeAssistant
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass, config):
    return True

def fetch_poe_data(host, username, password):
    session = requests.Session()
    cookie = md5((username + password).encode('utf-8')).hexdigest()
    session.cookies.set('admin', cookie)
    
    # First request: PoE data (Power, Voltage, Current, Port Status)
    status_url = f"http://{host}/pse_port.cgi"
    try:
        response = session.get(status_url, timeout=10)
    except Exception as err:
        _LOGGER.error("Connection error: %s", err)
        return {}
    if response.status_code != 200:
        _LOGGER.error("Error retrieving status from %s", host)
        return {}
    html = response.text
    matches = re.findall(
        r"<td>(Port \d+)</td>\s*<td>(Enable|Disable)</td>\s*<td>(On|Off)</td>\s*<td>.*?</td>\s*"
        r"<td>(\d*\.?\d+|-)</td>\s*<td>(\d+|-)</td>\s*<td>(\d+|-)</td>",
        html
    )
    data = {}
    # Create PoE data for ports 1-8 (only these ports have PoE)
    for i in range(1, 9):
        port_data = next((d for d in matches if f"Port {i}" in d), None)
        if port_data:
            _, status, power_on, power, voltage, current = port_data
            data[str(i)] = {
                "status": status,
                "power_on": power_on == "On",
                "power": float(power) if power != "-" and power_on == "On" else 0,
                "voltage": int(voltage) if voltage != "-" and power_on == "On" else 0,
                "current": int(current) if current != "-" and power_on == "On" else 0
            }
        else:
            data[str(i)] = {
                "status": "Disable",
                "power_on": False,
                "power": 0,
                "voltage": 0,
                "current": 0
            }
    
    # Second request: Link Status and Packet Counters from port.cgi?page=stats (for ports 1-9)
    stats_url = f"http://{host}/port.cgi?page=stats"
    try:
        response_stats = session.get(stats_url, timeout=10)
    except Exception as err:
        _LOGGER.error("Connection error (Stats): %s", err)
        return data
    if response_stats.status_code != 200:
        _LOGGER.error("Error retrieving stats from %s", host)
        return data
    html_stats = response_stats.text
    stats_matches = re.findall(
        r"<tr>\s*<td>(Port \d+)</td>\s*<td>.*?</td>\s*<td>(?:Link\s+)?(Up|Down)</td>\s*<td>(\d+)</td>\s*<td>(\d+)</td>\s*<td>(\d+)</td>\s*<td>(\d+)</td>\s*</tr>",
        html_stats
    )
    # Loop over ports 1 to 9
    for i in range(1, 10):
        port_name = f"Port {i}"
        stats_data = next((d for d in stats_matches if port_name in d), None)
        if stats_data:
            _, link_status, tx_good, tx_bad, rx_good, rx_bad = stats_data
            if str(i) not in data:
                data[str(i)] = {}
            data[str(i)].update({
                "link_status": link_status,
                "tx_good": int(tx_good),
                "tx_bad": int(tx_bad),
                "rx_good": int(rx_good),
                "rx_bad": int(rx_bad)
            })
        else:
            if str(i) not in data:
                data[str(i)] = {}
            data[str(i)].update({
                "link_status": "Down",
                "tx_good": 0,
                "tx_bad": 0,
                "rx_good": 0,
                "rx_bad": 0
            })
    
    # Third request: Extract Link Speed from port.cgi (without parameters) for ports 1-9
    control_url = f"http://{host}/port.cgi"
    try:
        response_control = session.get(control_url, timeout=10)
    except Exception as err:
        _LOGGER.error("Connection error (Control): %s", err)
    else:
        if response_control.status_code == 200:
            html_control = response_control.text
            speed_matches = re.findall(
                r"<tr>\s*<td>\s*Port\s*(\d+)\s*</td>\s*<td>[^<]+</td>\s*<td>[^<]+</td>\s*<td>\s*([^<]+)\s*</td>",
                html_control, re.DOTALL
            )
            for match in speed_matches:
                port_number = match[0].strip()
                actual_speed = match[1].strip()
                if port_number in data:
                    data[port_number]["link_speed"] = actual_speed
                else:
                    data[port_number] = {"link_speed": actual_speed}
        else:
            _LOGGER.error("Error retrieving control data from %s", host)
    
    # Fourth request: System Information from info.cgi
    info_url = f"http://{host}/info.cgi"
    system_info = {}
    try:
        response_info = session.get(info_url, timeout=10)
    except Exception as err:
        _LOGGER.error("Connection error (System Info): %s", err)
    else:
        if response_info.status_code != 200:
            _LOGGER.error("Error retrieving system info from %s", host)
        else:
            html_info = response_info.text
            info_match = re.search(r"(<fieldset>.*?</fieldset>)", html_info, re.DOTALL)
            if info_match:
                info_block = info_match.group(1)
            else:
                info_block = html_info
            model = re.search(r"<th\s*style=\"width:150px;\">Device Model</th>\s*<td\s*style=\"width:250px;\">([^<]+)</td>", info_block)
            mac = re.search(r"<th>MAC Address</th>\s*<td>([^<]+)</td>", info_block)
            ip_addr = re.search(r"<th>IP Address</th>\s*<td>([^<]+)</td>", info_block)
            netmask = re.search(r"<th>Netmask</th>\s*<td>([^<]+)</td>", info_block)
            gateway = re.search(r"<th>Gateway</th>\s*<td>([^<]+)</td>", info_block)
            firmware_version = re.search(r"<th>Firmware Version</th>\s*<td>([^<]+)</td>", info_block)
            firmware_date = re.search(r"<th>Firmware Date</th>\s*<td>([^<]+)</td>", info_block)
            hardware_version = re.search(r"<th>Hardware Version</th>\s*<td>([^<]+)</td>", info_block)
            system_info = {
                "model": model.group(1).strip() if model else None,
                "mac": mac.group(1).strip() if mac else None,
                "ip": ip_addr.group(1).strip() if ip_addr else None,
                "netmask": netmask.group(1).strip() if netmask else None,
                "gateway": gateway.group(1).strip() if gateway else None,
                "firmware_version": firmware_version.group(1).strip() if firmware_version else None,
                "firmware_date": firmware_date.group(1).strip() if firmware_date else None,
                "hardware_version": hardware_version.group(1).strip() if hardware_version else None,
            }
    data["system_info"] = system_info

    # Fifth request: Overall PoE Power Consumption from pse_system.cgi
    system_url = f"http://{host}/pse_system.cgi"
    try:
        response_system = session.get(system_url, timeout=10)
    except Exception as err:
        _LOGGER.error("Connection error (PSE System): %s", err)
    else:
        if response_system.status_code == 200:
            html_system = response_system.text
            consumption_match = re.search(r'name="pse_con_pwr"\s+value="([^"]+)"', html_system)
            if consumption_match:
                try:
                    overall_power = float(consumption_match.group(1).strip())
                except ValueError:
                    overall_power = 0
                data["overall_power"] = overall_power
            else:
                data["overall_power"] = 0
        else:
            _LOGGER.error("Error retrieving PSE system data from %s", host)
    
    return data

async def async_setup_entry(hass: HomeAssistant, entry):
    host = entry.data.get("host")
    username = entry.data.get("username")
    password = entry.data.get("password")
    scan_interval = entry.data.get("scan_interval", 30)
    has_poe = entry.data.get("Switch has PoE", True)

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="POE Data",
        update_method=lambda: hass.async_add_executor_job(fetch_poe_data, host, username, password),
        update_interval=timedelta(seconds=scan_interval),
    )

    await coordinator.async_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {"coordinator": coordinator, "config": entry.data}

    # Always forward sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    # Forward switch platform only if Switch has PoE is enabled (since PoE switches only have ports 1-8)
    if has_poe:
        await hass.config_entries.async_forward_entry_setups(entry, ["switch"])
    else:
        _LOGGER.info("Switch has PoE disabled - skipping switch platform setup")
    return True

async def async_unload_entry(hass: HomeAssistant, entry):
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor", "switch"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
