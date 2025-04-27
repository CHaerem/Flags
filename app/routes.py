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
    # Check for country in JSON body first, then form data, then query params
    country = None
    if request.is_json:
        data = request.get_json()
        country = data.get('country')
    elif request.form:
        country = request.form.get('country')
    else:
        country = request.args.get('country')
    
    if not country:
        return jsonify({'status': 'error', 'message': 'Country not provided'}), 400
    
    # Run the update flag script as the current user
    try:
        # Force cleanup the lock file if there were recent timeouts
        success = update_flag_safely(country, force_cleanup=True)
        
        if success == 0:
            return jsonify({'status': 'success', 'message': f'Flag changed to {country}'}), 200
        else:
            # The update_flag_safely function returned a non-zero exit code
            return jsonify({
                'status': 'partial_success', 
                'message': f'Flag metadata updated for {country}, but physical display may not have updated'
            }), 202
            
    except Exception as e:
        logging.error(f"Error changing flag: {str(e)}", exc_info=True)
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

@main.route('/config', methods=['POST'])
def save_config():
    # Import config_manager here to avoid circular imports
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts'))
    from config_manager import load_config, save_config
    
    # Load existing configuration
    config = load_config()
    
    # Update configuration from form data
    config['flag_display']['enabled'] = 'enabled' in request.form
    config['flag_display']['headless'] = 'headless' in request.form
    
    # Always use time-based scheduling
    config['flag_display']['use_fixed_times'] = True
    
    # Save time-based scheduling options
    config['flag_display']['time_interval'] = int(request.form.get('time_interval', 30))
    config['flag_display']['start_hour'] = int(request.form.get('start_hour', 0))
    config['flag_display']['start_minute'] = int(request.form.get('start_minute', 0))
    
    config['flag_display']['update_at_startup'] = 'update_at_startup' in request.form
    config['flag_display']['mode'] = request.form.get('display_mode', 'random')
    config['flag_display']['fixed_country'] = request.form.get('fixed_country', '')
    
    # Update display config
    config['display']['width'] = int(request.form.get('display_width', 800))
    config['display']['height'] = int(request.form.get('display_height', 480))
    
    # Save the configuration
    save_config(config)
    
    # Reload the configuration to ensure it was saved correctly
    config = load_config()
    
    # Render the config template with the updated configuration data
    return render_template('config.html', config=config, message="Configuration saved successfully!", success=True)

@main.route('/update-flag', methods=['POST'])
def update_flag_now():
    # Import update_flag
    try:
        # Force cleanup the lock file if there were recent timeouts and use random country
        success = update_flag_safely(None, force_cleanup=True)
        
        # Import config_manager to load the current configuration
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts'))
        from config_manager import load_config
        config = load_config()
        
        if success == 0:
            return render_template('config.html', config=config, message="Flag updated successfully!", success=True)
        else:
            return render_template('config.html', config=config, 
                                  message="Flag metadata updated, but physical display may not have updated.", 
                                  success=True)
            
    except Exception as e:
        logging.error(f"Error updating flag: {str(e)}", exc_info=True)
        # Import config_manager to load the current configuration
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts'))
        from config_manager import load_config
        config = load_config()
        
        return render_template('config.html', config=config, 
                              message=f"Error updating flag: {str(e)}", 
                              success=False)