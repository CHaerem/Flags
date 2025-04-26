#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
import subprocess
from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # allow requests from your docs site

@app.route("/change-flag", methods=["POST"])
def change_flag():
    country = request.args.get("country")
    if not country:
        return "Missing ?country=…", 400

    script = os.path.join(os.path.dirname(__file__), "main.py")
    cmd = ["sudo", "-u", "chris", "python3", script, country]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        return f"Error: {proc.stderr.strip()}", 500
    return f"Flag changed to {country}", 200

if __name__ == "__main__":
    # Start Flask API on HTTP for use with localtunnel
    app.run(host="0.0.0.0", port=5000)