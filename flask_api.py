#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
import subprocess
from flask import Flask, request, make_response, jsonify
from flask_cors import CORS

# Import the certificate generation function
from generate_cert import generate_self_signed_cert, cert_path, key_path

app = Flask(__name__)
# Allow GitHub Pages origins to make XHR/Fetch calls
CORS(app,
     resources={r"/change-flag": {"origins": ["https://chaerem.github.io", "https://*.github.io"]}},
     methods=["POST", "OPTIONS"],
     allow_headers=["Content-Type"],
     supports_credentials=False)

@app.route("/", methods=["GET"])
def health_check():
    """Health check endpoint that helps users to accept the certificate"""
    return jsonify({
        "status": "ok",
        "message": "API is running. If you're seeing this page, you can now return to the GitHub Pages site and use it.",
        "info": "This page helps your browser accept the self-signed certificate."
    })

@app.route("/change-flag", methods=["OPTIONS", "POST"])
def change_flag():
    # Respond to preflight immediately
    if request.method == "OPTIONS":
        resp = make_response(("", 204))
        resp.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
        resp.headers["Access-Control-Allow-Origin"] = "https://chaerem.github.io"
        return resp

    country = request.args.get("country")
    if not country:
        return "Missing ?country=…", 400

    script = os.path.join(os.path.dirname(__file__), "main.py")
    cmd = ["sudo", "-u", "chris", "python3", script, country]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        return f"Error: {proc.stderr.strip()}", 500
    resp = make_response(f"Flag changed to {country}", 200)
    resp.headers["Access-Control-Allow-Origin"] = "https://chaerem.github.io"
    return resp

if __name__ == "__main__":
    # Check if SSL certificates exist, generate if they don't
    if not os.path.exists(cert_path) or not os.path.exists(key_path):
        print("SSL certificates not found. Generating new certificates...")
        generate_self_signed_cert()
    
    print(f"Starting HTTPS server at https://0.0.0.0:5000/")
    print(f"Access locally via https://smartpi.local:5000/")
    print("CTRL+C to stop the server")
    
    # Start Flask with HTTPS
    app.run(host="0.0.0.0", port=5000, ssl_context=(cert_path, key_path))