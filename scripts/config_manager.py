#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Base directory of this project (~/Flags)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Config file path
CONFIG_FILE = os.path.join(BASE_DIR, "config", "config.json")

# Create a backup of the original config file if it doesn't exist
def _ensure_config_file():
    """Ensure config file exists with default values"""
    if not os.path.exists(CONFIG_FILE):
        default_config = {
            "flag_display": {
                "enabled": True,
                "update_interval_minutes": 30,
                "update_at_startup": True,
                "mode": "random",
                "fixed_country": "",
                "last_updated": "",
                "use_fixed_times": False,
                "time_interval": 30,
                "start_hour": 0,
                "start_minute": 0,
                "headless": False
            },
            "display": {
                "width": 800,
                "height": 480
            },
            "current_flag": {
                "country": "",
                "info": "",
                "emoji": "",
                "timestamp": ""
            }
        }
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(default_config, f, indent=2)
        logger.info(f"Created default config file at {CONFIG_FILE}")
        return default_config
    return None

def load_config():
    """Load configuration from file"""
    _ensure_config_file()
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        logger.debug("Loaded configuration from file")
        return config
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        # If there's an error, create a default config
        return _ensure_config_file()

def save_config(config):
    """Save configuration to file"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        logger.debug("Saved configuration to file")
        return True
    except Exception as e:
        logger.error(f"Error saving config: {e}")
        return False

def update_current_flag(config, country_data):
    """Update the current flag information in the config"""
    if not config or not country_data:
        return False
    
    config['current_flag'] = {
        "country": country_data['name']['common'] if 'name' in country_data and 'common' in country_data['name'] else "Unknown",
        "info": f"Capital: {country_data.get('capital', ['Unknown'])[0] if country_data.get('capital') else 'Unknown'}",
        "emoji": country_data.get('flag', ''),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Add extended information
    if 'population' in country_data:
        config['current_flag']['population'] = country_data['population']
    if 'region' in country_data:
        config['current_flag']['region'] = country_data['region']
    if 'subregion' in country_data:
        config['current_flag']['subregion'] = country_data['subregion']
    if 'languages' in country_data:
        config['current_flag']['languages'] = country_data['languages']
    if 'currencies' in country_data:
        config['current_flag']['currencies'] = country_data['currencies']
    if 'timezones' in country_data:
        config['current_flag']['timezones'] = country_data['timezones']
    
    # Update last_updated timestamp
    config['flag_display']['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Save the config
    save_config(config)
    return True

def get_flag_display_settings():
    """Get flag display settings from config"""
    config = load_config()
    return config.get('flag_display', {})

def update_flag_display_settings(settings):
    """Update flag display settings in config"""
    config = load_config()
    config['flag_display'].update(settings)
    return save_config(config)

def get_current_flag_info():
    """Get current flag information from config"""
    config = load_config()
    return config.get('current_flag', {})