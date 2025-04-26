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
from waveshare_epd import epd7in3f

logging.basicConfig(level=logging.DEBUG)

# Base directory of this project (~/Flags)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Paths for the new structure
CACHE_FILE     = os.path.join(BASE_DIR, "country_cache.json")
FLAG_CACHE_DIR = os.path.join(BASE_DIR, "flag_cache")
FLAG_INFO_PATH = os.path.join(BASE_DIR, "app", "static", "data", "flag.json")


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

    # If cache is empty, we should fetch data from API, but since we already have a populated country_cache.json,
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
    # For exact match
    if name in data:
        return data[name]
    
    # For case-insensitive match
    name_lower = name.lower()
    for country_name, country_data in data.items():
        if country_name.lower() == name_lower:
            return country_data
            
    # For partial match
    for country_name, country_data in data.items():
        if name_lower in country_name.lower() or country_name.lower() in name_lower:
            return country_data
            
    return None

def update_flag_metadata(country):
    # Build the metadata with comprehensive country information
    info = {
        "country": country['name']['common'] if 'name' in country and 'common' in country['name'] else "Unknown",
        "info": f"Capital: {country.get('capital', ['Unknown'])[0] if country.get('capital') else 'Unknown'}",
        "emoji": country.get('flag', ''),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Check if the country has extended information and add it to the metadata
    if 'population' in country:
        info['population'] = country['population']
    if 'region' in country:
        info['region'] = country['region']
    if 'subregion' in country:
        info['subregion'] = country['subregion']
    if 'languages' in country:
        info['languages'] = country['languages']
    if 'currencies' in country:
        info['currencies'] = country['currencies']
    if 'timezones' in country:
        info['timezones'] = country['timezones']

    # Ensure the directory exists, then write JSON
    os.makedirs(os.path.dirname(FLAG_INFO_PATH), exist_ok=True)
    with open(FLAG_INFO_PATH, 'w') as f:
        json.dump(info, f, indent=2)
    logging.info("Wrote metadata to %s", FLAG_INFO_PATH)

def display_flag(epd, country_name=None):
    logging.info("Displaying flag...")

    data = get_country_data()
    country = get_country_by_name(data, country_name) if country_name else None
    if country_name and not country:
        raise ValueError(f"Country '{country_name}' not recognized")
    if not country:
        # Select a random country from the dictionary
        random_key = random.choice(list(data.keys()))
        country = data[random_key]

    img = get_flag(country)
    
    # Update metadata
    update_flag_metadata(country)
    
    # Display the flag on the e-paper display
    resized = img.resize((epd.width, epd.height), Image.Resampling.LANCZOS)
    epd.display(epd.getbuffer(resized))
    logging.info(f"Displayed flag for {country['name']['common'] if 'name' in country and 'common' in country['name'] else 'Unknown'}")

if __name__ == "__main__":
    try:
        country_arg = sys.argv[1] if len(sys.argv) > 1 else None

        epd = epd7in3f.EPD()
        logging.info("Initializing display")
        epd.init()
        epd.Clear()

        display_flag(epd, country_arg)

        logging.info("Sleeping display")
        epd.sleep()

    except Exception as e:
        logging.error("Error: %s", e)
        traceback.print_exc()
        try:
            epd7in3f.epdconfig.module_exit()
        except:
            pass
        sys.exit(1)