import os
import json
import logging
from flask import Blueprint, request, jsonify, render_template, send_from_directory
import sys

# Create a Blueprint instance
main = Blueprint('main', __name__)

# Add scripts directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts'))

# Import update_flag_safely
try:
    from update_flag import update_flag_safely
except Exception as e:
    print(f"Error importing update_flag: {e}")

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@main.route('/change-flag', methods=['POST'])
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

@main.route('/config', methods=['GET'])
def get_config():
    # Import config_manager here to avoid circular imports
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts'))
    from config_manager import load_config
    
    # Load the configuration
    config = load_config()
    
    # Render the config template with the configuration data
    return render_template('config.html', config=config)