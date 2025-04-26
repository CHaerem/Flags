#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
import sys

# Add scripts directory to path so we can import from it
current_dir = os.path.dirname(os.path.abspath(__file__))
scripts_dir = os.path.join(current_dir, "scripts")
sys.path.append(scripts_dir)

from app import create_app
from generate_cert import generate_self_signed_cert, cert_path, key_path

# Create the Flask application
app = create_app()

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