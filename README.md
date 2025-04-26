# 🏳️‍🌈 E-Ink Flag Display with Self-Hosted Flask Server

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
   ./run.py
   ```

4. **Run the display script**

   ```bash
   sudo python3 main.py [CountryName]
   ```

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

     Then enable and start the service:

     ```bash
     sudo systemctl daemon-reload
     sudo systemctl enable flag-app
     sudo systemctl start flag-app
     ```

---

## 🎯 Features

- 📺 **E-Ink display** shows the current country's flag
- 🌐 **Self-hosted Flask app** serves the web interface and flag data
- 📱 **NFC tag** links directly to the Flask application
- 🗣️ **Google Home** voice control for flag changes and queries

---

## 📂 Project Structure

```
project-root/
├── run.py                      # Main Flask application entry point
├── main.py                     # Displays flag & updates metadata
├── app/                        # Flask application package
│   ├── __init__.py             # App initialization
│   ├── routes.py               # Routes definitions
│   ├── static/                 # Static assets
│   │   ├── css/                # Stylesheets
│   │   ├── js/                 # JavaScript files
│   │   └── data/               # Flag data
│   └── templates/              # HTML templates
├── flag_cache/                 # Downloaded flag images
└── docs/                       # Legacy GitHub Pages (deprecated)
```

---

## 💻 E-Ink Display (Raspberry Pi)

- Uses [`epd7in3f`](https://github.com/waveshare/e-Paper)
- **main.py**:
  1. Fetches country data & flag image (with caching)
  2. Resizes and displays on e-ink
  3. Writes metadata to `app/static/data/flag.json`
  4. (Optional) `git add && git commit && git push`

```json
// example flag.json
{
	"country": "Argentina",
	"info": "Capital: Buenos Aires",
	"emoji": "🇦🇷",
	"timestamp": "2025-04-25 14:30:00"
}
```

## 📱 NFC Integration

1. Install NFC Tools on your phone
2. Write URL `https://smartpi.local:5000/` to the tag
3. Tap the tag to open the flag info page

## 🗣️ Google Home (Local)

- **Flask API (run.py):**

  ```
  POST https://smartpi.local:5000/change-flag?country=Brazil
  ```

- **Local Home SDK (local-home-app.js):**
  - Sends POST /change-flag?country=XYZ to your Pi

## 🔄 Offline / Online Matrix

| Component     | Offline | Source                    |
| ------------- | ------- | ------------------------- |
| E-ink display | ✅      | Local on Raspberry Pi     |
| Web Interface | ✅      | Self-hosted Flask app     |
| Google Home   | ✅      | Local Home SDK → Pi       |
| NFC tag       | ✅      | Static HTTPS link to page |

## 🛠 To Do

- Support random flag rotation
- Add search functionality
- Implement dark/light theme toggle

---

## 👤 Author

Christopher Hærem  
📧 chris.haerem@gmail.com  
🔗 https://github.com/CHaerem

## Deployment Instructions

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
