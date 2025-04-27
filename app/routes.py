import os
import json
import logging
from flask import request, jsonify, render_template, send_from_directory
from app import app
import sys

# Add scripts directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts'))

# Import update_flag_safely
try:
    from update_flag import update_flag_safely
except Exception as e:
    print(f"Error importing update_flag: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/change-flag', methods=['POST'])
def change_flag():
    data = request.args
    country = data.get('country')
    
    if not country:
        return jsonify({'status': 'error', 'message': 'Country not provided'}), 400
    
    # Run the update flag script as the current user
    try:
        # Force cleanup the lock file if there were recent timeouts
        update_flag_safely(country, force_cleanup=True)
        return jsonify({'status': 'success', 'message': f'Flag changed to {country}'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/config', methods=['GET'])
def get_config():
    return render_template('config.html')