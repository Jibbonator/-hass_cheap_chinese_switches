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


## Installation

1. **Add the Integration via HACS:**  
   - Open Home Assistant and navigate to **HACS > Integrations**.  
   - Click the **"+"** button and select **"Custom Repository"**.  
   - Enter the repository URL:  
     `https://github.com/Jibbonator/-hass_cheap_chinese_switches`  
   - Select **"Integration"** as the repository type and click **"Add"**.  
   - Follow the on-screen instructions to install the integration, then restart Home Assistant.

2. **Manual Installation:**  
   - Copy the `cheap_chinese_switches` folder into your Home Assistant `custom_components` directory.
   - Restart Home Assistant.

## Configuration

During the initial setup, you will be prompted to provide:
- **Name:** A unique name for your switch.
- **Host:** The IP address or hostname of the switch.
- **Username & Password:** Credentials used to authenticate with the switch.
- **Switch has PoE:** Check if the switch supports PoE. (This option cannot be changed later.)
- **Polling Interval:** Choose between 10, 30, or 60 seconds.

If PoE is enabled, PoE-specific sensors (Port Power, Overall PoE Power) and switches will be created for ports 1–8. Regardless, link sensors for all 9 ports and network sensors (IP and Device MAC) are always created.

## Troubleshooting

- **Missing Entities:**  
  Verify that the repository structure is correct and that your switch returns valid data from the endpoints.
- **Polling Errors:**  
  Check the Home Assistant logs for connection errors or timeouts. The DataUpdateCoordinator ensures that each poll completes before the next one begins.
- **HACS Issues:**  
  Ensure your repository's default branch is set to `main` and that it is public.

## License

This project is licensed under the MIT License.

## Author

[@Jibbonator](https://github.com/Jibbonator)



Here are some Pictures:


The Look of the WebGui
![Screenshot 2025-02-28 194831](https://github.com/user-attachments/assets/d19dae85-f24f-48aa-9b93-fabebbb28a15)

Configuration

![Screenshot 2025-02-28 160018](https://github.com/user-attachments/assets/308bb417-3751-4657-b7f9-c789f8e069e9)

With POE
![Screenshot 2025-02-28 193502](https://github.com/user-attachments/assets/30f348f7-04ab-4a06-a574-5663f0da2184)

Without POE
![Screenshot 2025-02-28 193527](https://github.com/user-attachments/assets/fd182a85-b7b0-456e-89b2-4bbd658c2955)

The Attributes

![Screenshot 2025-02-28 195512](https://github.com/user-attachments/assets/ed9ae93b-a1aa-4742-8d48-7e603158f735)
