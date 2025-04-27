# 🏳️  E-Ink Flag Display with Self-Hosted Flask Server

## 🚀 Getting Started

1. **Clone the repo**

   ```bash
   git clone https://github.com/CHaerem/Flags.git
   cd Flags
   ```

2. **Install dependencies**

   ```bash
   # System packages
   sudo apt update
   sudo apt install python3-pip python3-venv python3-flask

   # (Optional) Create and use a virtual environment:
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Start the Flask server**

   ```bash
   # Run manually
   python3 run.py [--mock] [--headless] [--port PORT]
   ```
   - `--mock`: Use mock display (web preview, no hardware required)
   - `--headless`: Disable all display updates (metadata only)
   - `--port`: Specify server port (default from config)

4. **Run the display script directly**

   ```bash
   sudo python3 scripts/main.py [CountryName]
   ```
   - If no country is specified, will use config or random

5. **Auto-start on boot** (pick one):

   - **Cron**:
     ```bash
     crontab -e
     @reboot sleep 15 && /usr/bin/python3 /home/chris/Flags/run.py >> flask_api.log 2>&1
     ```
   - **systemd**:  
     Create `/etc/systemd/system/flag-app.service` with:

     ```
     [Unit]
     Description=Flag Display Flask App
     After=network.target

     [Service]
     User=chris
     WorkingDirectory=/home/chris/Flags
     ExecStart=/usr/bin/python3 /home/chris/Flags/run.py
     Restart=always

     [Install]
     WantedBy=multi-user.target
     ```

---

## 🆕 Key Features

- 📺 **E-Ink display** (Waveshare 7.3") or **Mock Display** (web preview)
- 🌐 **Modern Flask web UI** with flag info, autocomplete, and map
- 🖥️ **Configuration page**: Enable/disable updates, headless/mock modes, scheduling, display size
- 🔁 **Flexible scheduling**: Time-based intervals, fixed update times, update at startup
- 🔍 **Autocomplete** for country selection (with emoji, offline)
- 🗺️ **World map**: Shows location of selected country
- 🛠 **Manual/automatic flag update** via web or API
- 🔄 **Offline/Online**: All core features work offline on local network
- 🛡️ **Display lock**: Prevents hardware conflicts
- 📱 **NFC tag** and 🗣️ **Google Home** integration (see below)

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
