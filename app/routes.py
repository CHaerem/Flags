import os
import json
import subprocess
import sys
from flask import Blueprint, render_template, request, jsonify, make_response, current_app, send_from_directory, redirect, url_for

# Add scripts directory to path so we can import from it
current_dir = os.path.dirname(os.path.abspath(__file__))
scripts_dir = os.path.join(os.path.dirname(current_dir), "scripts")
sys.path.append(scripts_dir)

# Import configuration manager
from scripts.config_manager import load_config, save_config, update_flag_display_settings

# Create blueprint
main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@main.route('/config', methods=['GET', 'POST'])
def config():
    """Configuration page for flag display settings"""
    message = None
    success = False
    
    # Load the current configuration
    config = load_config()
    
    if request.method == 'POST':
        try:
            # Update flag display settings
            flag_settings = {
                'enabled': 'enabled' in request.form,
                'headless': 'headless' in request.form,  # Add headless mode option
                'update_interval_minutes': int(request.form.get('update_interval', 30)),
                'update_at_startup': 'update_at_startup' in request.form,
                'mode': request.form.get('display_mode', 'random'),
                'fixed_country': request.form.get('fixed_country', '')
            }
            
            # Update display settings
            config['display'] = {
                'width': int(request.form.get('display_width', 800)),
                'height': int(request.form.get('display_height', 480))
            }
            
            # Update the configuration
            config['flag_display'] = flag_settings
            save_config(config)
            
            message = "Configuration saved successfully! Restart the service for changes to take effect."
            success = True
            
            # Reload the configuration to get the updated values
            config = load_config()
        except Exception as e:
            message = f"Error saving configuration: {str(e)}"
            success = False
    
    # Render the configuration page with the current settings
    return render_template('config.html', config=config, message=message, success=success)

@main.route('/update-flag', methods=['POST'])
def update_flag_now():
    """Manually trigger a flag update"""
    try:
        # Get the base directory path
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        script = os.path.join(base_dir, "scripts", "main.py")
        
        # Run the script to update the flag
        cmd = ["python3", script]
        
        # If we're on a Raspberry Pi or Linux system, use sudo
        if os.name != "nt":  # Not Windows
            cmd = ["sudo", "-u", "chris", "python3", script]
            
        proc = subprocess.run(cmd, capture_output=True, text=True)
        
        if proc.returncode != 0:
            return redirect(url_for('main.config', message=f"Error updating flag: {proc.stderr.strip()}", success=False))
        
        return redirect(url_for('main.config', message="Flag updated successfully!", success=True))
    except Exception as e:
        return redirect(url_for('main.config', message=f"Error updating flag: {str(e)}", success=False))

@main.route('/static/data/flag.json')
def flag_json():
    """Serve the flag.json data file"""
    try:
        # First try the config file
        config = load_config()
        if config and 'current_flag' in config and config['current_flag'].get('country'):
            return jsonify(config['current_flag'])
            
        # Fallback to current_flag.json for backward compatibility
        current_flag_path = os.path.join(current_app.root_path, '..', 'current_flag.json')
        
        if os.path.exists(current_flag_path):
            # Read the content of current_flag.json and return it
            with open(current_flag_path, 'r') as f:
                flag_data = json.load(f)
                return jsonify(flag_data)
        else:
            return jsonify({"error": "Flag data not found"}), 404
            
    except Exception as e:
        current_app.logger.error(f"Error serving flag data: {str(e)}")
        return jsonify({"error": "Failed to load flag data"}), 500

@main.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "message": "API is running. Static site is served directly from this Flask application."
    })

@main.route("/change-flag", methods=["OPTIONS", "POST"])
def change_flag():
    """Change the displayed flag"""
    # Respond to preflight immediately
    if request.method == "OPTIONS":
        resp = make_response(("", 204))
        resp.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
        resp.headers["Access-Control-Allow-Origin"] = "*"
        return resp

    country = request.args.get("country")
    if not country:
        return "Missing ?country=…", 400

    # Get the base directory path
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    script = os.path.join(base_dir, "scripts", "main.py")
    
    # Run the script to change the flag
    cmd = ["sudo", "-u", "chris", "python3", script, country]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    
    if proc.returncode != 0:
        return f"Error: {proc.stderr.strip()}", 500
    
    # Prepare response
    resp = make_response(f"Flag changed to {country}", 200)
    resp.headers["Access-Control-Allow-Origin"] = "*"
    
    return resp