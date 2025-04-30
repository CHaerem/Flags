# 🏳️ E-Ink Flag Display (Flask)

A modern, self-hosted Flask app to control a Waveshare E-Ink display (or web mock) showing the flag of any country. Supports Google Home voice control, IFTTT, and secure or local API access.

---

## 🚀 Quick Start

1. **Clone & Install**
   ```bash
   git clone https://github.com/CHaerem/Flags.git
   cd Flags
   sudo apt update && sudo apt install python3-pip python3-venv python3-flask
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. **Run the Flask server**
   ```bash
   python3 run.py [--mock] [--headless] [--port PORT]
   ```
   - `--mock`: Web preview (no hardware)
   - `--headless`: Metadata only (no display)
3. **(Optional) Run display script directly**
   ```bash
   sudo python3 scripts/main.py [CountryName]
   ```
4. **Auto-start on boot**
   - **Cron**: Add to `crontab -e`
   - **systemd**: See example below

---

## ✨ Features
- **Real or Mock Display**: E-Ink hardware or browser preview
- **Modern Web UI**: Flag info, autocomplete, map
- **Configurable**: Enable/disable, mock/headless, schedule, display size
- **Flexible Scheduling**: Time-based intervals, update at startup
- **Offline/Online**: Works on your LAN or via Tailscale
- **API & Voice Control**: Secure or local endpoints, Google Home/IFTTT
- **Display Lock**: Prevents hardware conflicts

---

## 🔒 API Endpoints (Summary)
| Endpoint                | Access         | Auth Required     | Purpose                |
|------------------------|---------------|-------------------|------------------------|
| `/change-flag`         | Public (Funnel)| Yes (`X-Flag-Token`)| Change flag remotely   |
| `/local-change-flag`   | Local only     | No                | Change flag locally    |
| `/current-flag`        | Public/Local   | No                | Get current flag info  |

> **Only `/change-flag` is exposed via Tailscale Funnel for secure remote/IFTTT use. Local web UI/scripts use `/local-change-flag` (open on LAN). `/current-flag` is always open.**

     with header:
     > X-Flag-Token: your-secret-token

5. **Local Access**
   - For local scripts or web UI, use:
     > http://FlagPi.local/local-change-flag
   - No token required for local use.

6. **Get Current Flag Info**
   - Anyone (local or remote) can GET:
     > http://FlagPi.local/current-flag
     > https://flagpi.ts.net/current-flag

**✅ Result:**
- Google Home speaks your command
- IFTTT sends the flag update
- Tailscale securely delivers it to your Pi (with token)
- Flask accepts the request and updates the E-Ink flag display

---

**Summary:**
- **Remote/public updates**: `/change-flag` (secure, token required)
- **Local updates**: `/local-change-flag` (open)
- **Flag info**: `/current-flag` (open)

*Let me know if you’d like a diagram or script to automate this setup!*

---

## 📂 Project Structure

```
project-root/
├── run.py                      # Main Flask server entry point
├── scripts/
│   ├── main.py                 # Flag display & metadata update logic
│   ├── config_manager.py       # Config and state management
│   └── ...                     # Other utility scripts
├── app/                        # Flask application package
│   ├── __init__.py             # App initialization
│   ├── routes.py               # API and web routes
│   ├── static/                 # Static assets (css, js, data)
│   │   ├── css/
│   │   ├── js/                 # UI, autocomplete, map
│   │   └── data/               # Country/flag JSON
│   └── templates/              # HTML templates (index, config, preview)
├── display/                    # Display drivers (e-ink, mock)
│   ├── manager.py, lock.py, ...
├── flag_cache/                 # Downloaded flag images
├── requirements.txt            # Python dependencies
└── ...
```

---


     Then enable and start the service:

     ```bash
     sudo systemctl daemon-reload
     sudo systemctl enable flag-app
     sudo systemctl start flag-app
     ```

---

## ⚙️ Configuration & Modes

- Access `/config` in the web UI to:
  - Enable/disable flag updates
  - Switch between **physical display**, **mock display** (web preview), or **headless** (metadata only)
  - Set update interval (15 min, 30 min, 1h, ...)
  - Choose fixed/random country or update at startup
  - Adjust display width/height
  - Manually trigger flag update
  - See current flag info

### Mock Display & Preview
- Use `--mock` or enable mock mode in config to preview the e-ink display in the browser (`/preview`)
- No hardware required for mock mode (great for development/testing)

### Headless Mode
- Use `--headless` or enable in config to only update metadata (no display access)
- Useful for troubleshooting or running on non-Pi systems

### Autocomplete & Map
- Country input fields use offline autocomplete with emoji flags
- The web UI shows a world map and highlights the selected country

### API Endpoints
- `POST /change-flag` (JSON or form): Change displayed flag
- `POST /update-flag`: Force update (random or config country)
- `GET /config`: View config page

---

## 💻 E-Ink & Mock Display

- **Physical e-ink display** (Waveshare 7.3") supported on Raspberry Pi
- **Mock display** provides a web preview for any system
- **Display lock** ensures safe access (prevents hardware conflicts)

---

## 🗂 Example flag.json
```json
{
  "country": "Argentina",
  "info": "Capital: Buenos Aires",
  "emoji": "🇦🇷",
  "timestamp": "2025-04-25 14:30:00",
  "population": 45376763,
  "region": "Americas",
  "subregion": "South America",
  "languages": {"spa": "Spanish"},
  "currencies": {"ARS": {"symbol": "$", "name": "Argentine peso"}},
  "timezones": ["UTC-03:00"]
}
```

---

## 📱 NFC Integration

- **NFC**: Write your Pi's web URL to an NFC tag for instant access
- **Google Home**: *(Planned feature, not yet implemented)*

---

## 🔄 Offline/Online Matrix

| Component     | Offline | Source                    |
| ------------- | ------- | ------------------------- |
| E-ink display | ✅      | Local on Raspberry Pi     |
| Web Interface | ✅      | Self-hosted Flask app     |
| Google Home   | 🚧      | *(Planned, not available)*|
| NFC tag       | ✅      | Static HTTPS link to page |

---

## 🛠 To Do
- Add more scheduling options
- Improve dark/light theme
- More map features
- Multi-language support

---

## 👤 Author

Christopher Hærem  
📧 chris.haerem@gmail.com  
🔗 https://github.com/CHaerem

---

## 📝 Deployment & Troubleshooting

- See above for systemd/cron setup for auto-start
- Logs: check `flask_api.log` or use `journalctl -u flag-app`
- For troubleshooting, try `--mock` or `--headless` to isolate issues
- All configuration can be managed through `/config` in the web UI

If the application isn't working as expected:

1. Check the service logs:

   ```bash
   sudo journalctl -u flag-app
   tail -f flask_api.log
   ```
2. Try running in mock/headless mode to debug
3. Ensure all dependencies are installed (see requirements.txt)
4. For hardware issues, check display cables and power

---


To deploy the flag display application to your Raspberry Pi:

1. Copy all project files to your Pi (e.g., `/home/chris/Flags/`)

2. Install required dependencies:

   ```bash
   pip3 install -r requirements.txt
   ```

3. Make sure the startup script is executable:

   ```bash
   chmod +x run.py
   ```

4. Test that the application runs correctly:

   ```bash
   python3 run.py
   ```

5. Install the systemd service:

   ```bash
   sudo cp config/flag-api.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable flag-api.service
   sudo systemctl start flag-api.service
   ```

6. Check the service status:

   ```bash
   sudo systemctl status flag-api.service
   ```

7. Access the web interface at `http://smartpi.local:5000/` from your local network.

### Updating the Application

If you need to update the application:

1. Copy the updated files to the Pi
2. Restart the service:
   ```bash
   sudo systemctl restart flag-api.service
   ```

### Troubleshooting

If the application isn't working as expected:

1. Check the service logs:

   ```bash
   sudo journalctl -u flag-api.service -n 50
   ```

2. Check if the service is running:

   ```bash
   sudo systemctl status flag-api.service
   ```

3. Ensure the country data is correctly prepared by checking if `/home/chris/Flags/app/static/data/countries.json` exists
