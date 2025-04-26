#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
import subprocess
from flask import Flask, request, make_response
from flask_cors import CORS

app = Flask(__name__)
# Allow GitHub Pages origins to make XHR/Fetch calls
CORS(app,
     resources={r"/change-flag": {"origins": ["https://chaerem.github.io", "https://*.github.io"]}},
     methods=["POST", "OPTIONS"],
     allow_headers=["Content-Type"],
     supports_credentials=False)

@app.route("/change-flag", methods=["OPTIONS", "POST"])
def change_flag():
    # Respond to preflight immediately
    if request.method == "OPTIONS":
        resp = make_response(("", 204))
        resp.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return resp

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
    # HTTP on 5000 for localtunnel
    app.run(host="0.0.0.0", port=5000)