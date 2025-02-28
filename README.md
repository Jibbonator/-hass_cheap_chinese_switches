# Cheap Chinese Switches Integration

I´m not a Programmer myself. I created this only using chatGPT

This custom integration supports various PoE switches commonly found in budget devices.
I used a Keeplink KP-9000-9XHML-X and a KP-9000-9XHPML-X-AC.
Maybe it can work with other cheap China Switches too.
I wanted a way to Switch Poe ON/from from Homeassistant and see the Poe consumption.

This is the actual state:

It polls multiple endpoints on the switch to extract data such as power consumption, port status, link speed, and system information, then exposes these values as Home Assistant entities (sensors and switches).

## Features

- **Multiple Data Sources:**  
  - **`/pse_port.cgi`:** Retrieves PoE data (power, voltage, current, port status) for ports 1–8.
  - **`/port.cgi?page=stats`:** Extracts link status (Up/Down) and packet counters (tx_good, tx_bad, rx_good, rx_bad) for ports 1–9.
  - **`/port.cgi`:** Extracts the actual link speed from the port settings table for ports 1–9.
  - **`/pse_system.cgi`:** Retrieves overall PoE power consumption from the input field `pse_con_pwr`.
  - **`/info.cgi`:** Retrieves system information such as device model, MAC address, IP address, netmask, gateway, firmware version, firmware date, and hardware version.

- **Entity Creation:**  
  - **Switch Entities:**  
    - Creates switches (named "Port X PoE") for PoE-enabled ports (1–8) if PoE is enabled.
    - Dynamic icons are provided (using `mdi:power-plug` when on and `mdi:power-plug-off` when off).
  - **Sensor Entities:**  
    - **Port Power Sensor:** Displays the power consumption for each PoE port with voltage and current as attributes.
    - **Port Link Sensor:** Displays the link status for each port (ports 1–9) along with packet counters and link speed.
    - **Overall PoE Power Sensor:** Shows the overall PoE power consumption (only created if PoE is enabled).
    - **Network Sensors:**  
      - **IP Address Sensor:** Displays the switch's IP address with netmask and gateway as attributes.
      - **Device MAC Sensor:** Displays the switch's MAC address.

- **Configurable Polling:**  
  Uses Home Assistant’s `DataUpdateCoordinator` to poll the switch at a configurable interval. You can choose between 10, 30, or 60 seconds.

- **Initial Setup Option:**  
  During the initial configuration, you can select whether the switch has PoE ("Switch has PoE"). Once set, this option cannot be changed later.

## Repository Structure

The repository must have the following structure for HACS compatibility:

