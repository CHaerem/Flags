#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
import sys

# Add scripts directory to path so we can import from it
current_dir = os.path.dirname(os.path.abspath(__file__))
scripts_dir = os.path.join(current_dir, "scripts")
sys.path.append(scripts_dir)

# Import the prepare_country_data function
from prepare_country_data import prepare_country_data
from app import create_app

# Create the Flask application
app = create_app()

if __name__ == "__main__":
    # Prepare country data at startup
    print("Preparing country data...")
    if prepare_country_data():
        print("Country data prepared successfully!")
    else:
        print("Warning: Failed to prepare country data")
    
    print(f"Starting server at http://0.0.0.0:5000/")
    print(f"Access locally via http://smartpi.local:5000/")
    print("CTRL+C to stop the server")
    
    # Start Flask without HTTPS
    app.run(host="0.0.0.0", port=5000)