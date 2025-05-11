#!/usr/bin/python
# -*- coding:utf-8 -*-

import sys
import os
import random
import logging
import json
import time
import subprocess
import traceback
from io import BytesIO

import requests
from PIL import Image

# Import the config manager
from config_manager import load_config, update_current_flag, get_flag_display_settings
# Import the display lock
from display_lock import DisplayLock

logging.basicConfig(level=logging.DEBUG)

# Base directory of this project (~/Flags)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Paths for the new structure
CACHE_FILE     = os.path.join(BASE_DIR, "app", "static", "data", "countries.json")
FLAG_CACHE_DIR = os.path.join(BASE_DIR, "flag_cache")
FLAG_INFO_PATH = os.path.join(BASE_DIR, "app", "static", "data", "flag.json")

# Try to import e-paper display library, but handle case when not available
try:
    from waveshare_epd import epd7in3f
    EPD_AVAILABLE = True
except (ImportError, RuntimeError, ModuleNotFoundError) as e:
    logging.warning(f"E-paper display module not available: {e}")
    EPD_AVAILABLE = False


def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_cache(data):
    with open(CACHE_FILE, 'w') as f:
        json.dump(data, f)

def get_country_data():
    cache = load_cache()
    if cache:
        logging.info("Loaded country data from cache")
        return cache

    # If cache is empty, we should fetch data from API, but since we already have a populated countries.json,
    # this probably won't happen unless the file is deleted
    url = "https://restcountries.com/v3.1/all?fields=name,flags,capital,flag,population,region,subregion,languages,currencies,timezones"
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    
    # Convert array to dictionary with country names as keys
    country_dict = {}
    for country in data:
        country_dict[country['name']['common']] = country
    
    save_cache(country_dict)
    logging.info("Fetched country data and saved to cache")
    return country_dict

def load_flag_cache(code):
    os.makedirs(FLAG_CACHE_DIR, exist_ok=True)
    fname = os.path.join(FLAG_CACHE_DIR, f"{code.lower()}.png")
    if os.path.exists(fname):
        return Image.open(fname)
    return None

def save_flag_cache(code, img):
    os.makedirs(FLAG_CACHE_DIR, exist_ok=True)
    fname = os.path.join(FLAG_CACHE_DIR, f"{code.lower()}.png")
    img.save(fname)

def get_flag(country_data):
    # First try to use the country code (cca2) if available
    code = country_data.get('cca2', '')
    if code:
        cached = load_flag_cache(code)
        if cached:
            logging.info(f"Loaded flag image for {code} from cache")
            return cached
    
    # If no code or cached image, use the flag image from the flag_cache directory if it exists
    # Otherwise try to download from the flags.png URL if available
    if 'flags' in country_data and 'png' in country_data['flags']:
        url = country_data['flags']['png']
        try:
            headers = {'User-Agent': 'Mozilla/5.0', 'Accept': 'image/png'}
            resp = requests.get(url, headers=headers)
            resp.raise_for_status()
            img = Image.open(BytesIO(resp.content))
            if code:
                save_flag_cache(code, img)
                logging.info(f"Fetched flag image for {code} and saved to cache")
            return img
        except Exception as e:
            logging.error(f"Failed to get flag image from URL: {e}")
    
    # If all else fails, try to find a png file in the flag_cache directory that matches the first two letters of the country name
    country_name = country_data['name']['common']
    potential_code = ''.join(c for c in country_name if c.isalpha())[:2].lower()
    cached = load_flag_cache(potential_code)
    if cached:
        logging.info(f"Found flag image for {country_name} using code {potential_code}")
        return cached
    
    raise ValueError(f"Could not find or fetch flag image for {country_name}")

def get_country_by_name(data, name):
    if not name:
        return None
    
    # Normalize input    
    name_lower = name.lower().strip()
    
    # Try direct match with key (case insensitive)
    for country_name, country_data in data.items():
        if country_name.lower() == name_lower:
            logging.info(f"Found direct match for '{name}': {country_name}")
            return country_data
    
    # Try exact match with flag emoji (many users might paste emoji)
    for country_name, country_data in data.items():
        if country_data.get('flag', '').lower() == name_lower:
            logging.info(f"Found emoji match for '{name}': {country_name}")
            return country_data
    
    # Try match with common alternative names
    alt_names = {
        'usa': 'United States',
        'us': 'United States',
        'america': 'United States',
        'uk': 'United Kingdom',
        'england': 'United Kingdom',
        'britain': 'United Kingdom',
        'uae': 'United Arab Emirates',
        'roc': 'Taiwan',
        'drc': 'DR Congo',
        'north macedonia': 'Macedonia',
        'macedonia': 'North Macedonia',
    }
    
    if name_lower in alt_names:
        alt_name = alt_names[name_lower]
        if alt_name in data:
            logging.info(f"Found alternative name match: '{name}' -> '{alt_name}'")
            return data[alt_name]
    
    # Try partial match - if the input is contained in any country name
    for country_name, country_data in data.items():
        if name_lower in country_name.lower():
            logging.info(f"Found partial match for '{name}': {country_name}")
            return country_data
    
    # Try partial match - if any country name is contained in the input
    for country_name, country_data in data.items():
        if country_name.lower() in name_lower:
            logging.info(f"Found reverse partial match for '{name}': {country_name}")
            return country_data
    
    # Try country codes (cca2, cca3)
    for country_name, country_data in data.items():
        cca2 = country_data.get('cca2', '').lower()
        cca3 = country_data.get('cca3', '').lower()
        if cca2 == name_lower or cca3 == name_lower:
            logging.info(f"Found country code match for '{name}': {country_name}")
            return country_data
    
    logging.warning(f"No matching country found for '{name}'")
    return None

# Updated to use the config_manager
def update_flag_metadata(country):
    # Load the config
    config = load_config()
    
    # Update the current flag information in the config
    update_current_flag(config, country)
    
    # Also update the FLAG_INFO_PATH for backward compatibility
    os.makedirs(os.path.dirname(FLAG_INFO_PATH), exist_ok=True)
    with open(FLAG_INFO_PATH, 'w') as f:
        json.dump(config['current_flag'], f, indent=2)
    
    logging.info(f"Updated flag metadata for {country['name']['common']}")

def display_flag(epd=None, country_name=None):
    logging.info("Displaying flag...")
    
    # Load configuration
    config = load_config()
    settings = config.get('flag_display', {})
    headless_mode = settings.get('headless', False)

    # Get country data
    data = get_country_data()
    
    # Check if we're using a specific country from the config
    if not country_name and settings.get('mode') == 'fixed' and settings.get('fixed_country'):
        country_name = settings.get('fixed_country')
        logging.info(f"Using fixed country from config: {country_name}")

    # Get the country
    country = get_country_by_name(data, country_name) if country_name else None
    if country_name and not country:
        logging.warning(f"Country '{country_name}' not recognized, using random country instead")
        country = None
        
    if not country:
        # Select a random country from the dictionary
        random_key = random.choice(list(data.keys()))
        country = data[random_key]
        logging.info(f"Selected random country: {country['name']['common']}")

    # Get the flag image
    img = get_flag(country)
    
    # Update metadata
    update_flag_metadata(country)
    
    # If we're in headless mode or e-paper display is not available, we just update the metadata
    if headless_mode or not EPD_AVAILABLE or epd is None:
        logging.info(f"Running in headless mode - metadata updated for {country['name']['common']}")
        return country
    
    # If we reach here, we have a valid epd instance and should update the physical display
    # Use a display lock to prevent concurrent access to GPIO pins
    with DisplayLock() as lock:
        if not lock.acquired:
            logging.warning("Could not acquire display lock, skipping physical display update")
            return country
            
        try:
            # Adjust display size based on config if available
            display_width = config.get('display', {}).get('width', epd.width)
            display_height = config.get('display', {}).get('height', epd.height)
            
            # Display the flag on the e-paper display
            resized = img.resize((display_width, display_height), Image.Resampling.LANCZOS)
            epd.display(epd.getbuffer(resized))
            logging.info(f"Displayed flag for {country['name']['common']}")
            
            # Put the display to sleep
            epd.sleep()
        except Exception as e:
            logging.error(f"Error updating display: {e}")
            traceback.print_exc()
            # Even if display fails, we've at least updated the metadata
    
    return country

if __name__ == "__main__":
    try:
        country_arg = sys.argv[1] if len(sys.argv) > 1 else None

        # Check if we should run in headless mode (either from config or command line)
        config = load_config()
        headless = config.get('flag_display', {}).get('headless', False)
        if "--headless" in sys.argv:
            headless = True

        if headless or not EPD_AVAILABLE:
            # Headless mode - just update metadata
            logging.info("Running in headless mode")
            display_flag(None, country_arg)
        else:
            # Normal mode with e-paper display
            # Use a display lock to prevent concurrent access to GPIO pins
            with DisplayLock() as lock:
                if not lock.acquired:
                    logging.warning("Could not acquire display lock, running in headless mode")
                    display_flag(None, country_arg)
                    sys.exit(0)
                    
                try:
                    epd = epd7in3f.EPD()
                    logging.info("Initializing display")
                    epd.init()
                    epd.Clear()

                    display_flag(epd, country_arg)
                    
                    logging.info("Sleeping display")
                    epd.sleep()
                except Exception as e:
                    logging.error(f"Display error: {e}")
                    # If the display fails, fall back to headless mode
                    display_flag(None, country_arg)
                
    except Exception as e:
        logging.error("Error: %s", e)
        traceback.print_exc()
        try:
            if 'epd' in locals() and epd and EPD_AVAILABLE:
                epd7in3f.epdconfig.module_exit()
        except:
            pass
        sys.exit(1)