#!/usr/bin/python
# -*- coding:utf-8 -*-

from flask import Flask, request
import subprocess
import os

app = Flask(__name__)

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
    app.run(host="0.0.0.0", port=5000)
