
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


