# 🏳️‍🌈 E-Ink Flag Display with NFC, GitHub Pages, and Google Home

This project runs on a Raspberry Pi with a Waveshare 7.3" e-ink display. It shows a national flag, updates a GitHub Pages-hosted info page, and supports interaction via NFC and Google Home voice commands.

---

## 🎯 Features

- 📺 **E-Ink display** shows the current country's flag
- 🌐 **GitHub Pages** serves a public `flag.json` with metadata
- 📱 **NFC tag** links directly to the GitHub-hosted page
- 🗣️ **Google Home** voice control for flag changes and queries

---

## 📂 Project Structure

```
project-root/
├── main.py                     # Displays flag & updates GitHub metadata
├── flask_api.py                # /change-flag endpoint for local control
├── flags/                      # .bmp images for each country
├── github-pages/
│   ├── index.html              # Public info page
│   ├── data/flag.json          # Current flag metadata
│   └── script.js               # Renders JSON into HTML
├── local-home-app/
│   └── local-home-app.js       # Google Local Home SDK logic
└── README.md
```

---

## 💻 E-Ink Display (Raspberry Pi)

- Uses [`epd7in3f`](https://github.com/waveshare/e-Paper)
- **main.py**:
  1. Fetches country data & flag image (with caching)
  2. Resizes and displays on e-ink
  3. Writes metadata to `github-pages/data/flag.json`
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
2. Write URL https://CHaerem.github.io/Flags/ to the tag
3. Tap the tag to open the flag info page

## 🗣️ Google Home (Local)

- **Flask API (flask_api.py):**

  ```
  POST http://raspberrypi.local:5000/change-flag?country=Brazil
  ```

- **Local Home SDK (local-home-app.js):**
  - Sends POST /change-flag?country=XYZ to your Pi
  - Fetches https://CHaerem.github.io/Flags/data/flag.json

## 🔄 Offline / Online Matrix

| Component     | Offline | Source                    |
| ------------- | ------- | ------------------------- |
| E-ink display | ✅      | Local on Raspberry Pi     |
| GitHub Pages  | ✅      | Public via GitHub         |
| Google Home   | ✅      | Local Home SDK → Pi       |
| NFC tag       | ✅      | Static HTTPS link to page |

## 🛠 To Do

- Add timestamp to flag.json
- Support random flag rotation
- Enable local preview of GitHub page

## 👤 Author

Christopher Hærem  
📧 chris.haerem@gmail.com  
🔗 https://github.com/CHaerem
