#!/usr/bin/python
# -*- coding:utf-8 -*-

from flask import Flask, request
from flask_cors import CORS
import subprocess
import os

app = Flask(__name__)
# Enable CORS for all domains to allow requests from GitHub Pages
CORS(app)

@app.route("/change-flag", methods=["POST"])
def change_flag():
    country = request.args.get("country")
    if not country:
        return "Missing ?country=…", 400

    script = os.path.join(os.path.dirname(__file__), "main.py")
    cmd = ["sudo", "-u", "chris", "python", script, country]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        return f"Error: {proc.stderr}", 500
    return f"Flag changed to {country}", 200

if __name__ == "__main__":
    # Path to the SSL certificate and key
    cert_path = os.path.join(os.path.dirname(__file__), 'cert.pem')
    key_path = os.path.join(os.path.dirname(__file__), 'key.pem')
    
    # Check if certificate files exist, otherwise provide instructions
    if not os.path.exists(cert_path) or not os.path.exists(key_path):
        print("SSL certificate files not found!")
        print("Create them by running this command on your Raspberry Pi:")
        print("openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365")
        print("This will create self-signed certificates that will last for 1 year")
    else:
        # Run the Flask app with HTTPS
        app.run(host="0.0.0.0", port=5000, ssl_context=(cert_path, key_path))
