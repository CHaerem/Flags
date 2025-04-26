#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
from waveshare_epd import epd7in3f
import random
import logging
import urllib
import json

import requests
from io import BytesIO
from PIL import Image

import time
from PIL import Image,ImageDraw,ImageFont
import traceback

logging.basicConfig(level=logging.DEBUG)

import requests
from io import BytesIO
from urllib.request import urlopen
from PIL import Image

import subprocess
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FLAG_INFO_PATH = os.path.join(BASE_DIR, "github-pages", "data", "flag.json")

# Update paths to use relative paths in the current directory
CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "country_cache.json")
FLAG_CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "flag_cache")

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return None

def save_cache(data):
    with open(CACHE_FILE, 'w') as f:
        json.dump(data, f)

def get_country_data():
    cache = load_cache()
    if cache:
        logging.info("Loaded country data from cache")
        return cache

    response = requests.get("https://restcountries.com/v3.1/all?fields=name,flags,capital,flag")
    data = response.json()
    save_cache(data)
    logging.info("Fetched country data from API and saved to cache")
    return data

def load_flag_cache(flag_url):
    if not os.path.exists(FLAG_CACHE_DIR):
        os.makedirs(FLAG_CACHE_DIR)
    flag_filename = os.path.join(FLAG_CACHE_DIR, os.path.basename(flag_url))
    if os.path.exists(flag_filename):
        return Image.open(flag_filename)
    return None

def save_flag_cache(flag_url, flag_image):
    flag_filename = os.path.join(FLAG_CACHE_DIR, os.path.basename(flag_url))
    flag_image.save(flag_filename)

def get_flag(flag_url):
    cached_flag = load_flag_cache(flag_url)
    if cached_flag:
        logging.info("Loaded flag image from cache")
        return cached_flag

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-us,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

    response = requests.get(flag_url, headers=headers)

    if response.status_code == 200:
        flag_image = Image.open(BytesIO(response.content))
        save_flag_cache(flag_url, flag_image)
        logging.info("Fetched flag image from URL and saved to cache")
        return flag_image
    else:
        raise Exception(f"Error {response.status_code}: {response.reason}")

def get_country_by_name(data, country_name):
    for item in data:
        if item['name']['common'].lower() == country_name.lower():
            return item
    return None

def update_flag_metadata(country):
    info = {
        "country": country['name']['common'],
        "info": f"Capital: {country.get('capital', ['Unknown'])[0]}",
        "emoji": country.get('flag', ''),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    os.makedirs(os.path.dirname(FLAG_INFO_PATH), exist_ok=True)
    with open(FLAG_INFO_PATH, 'w') as f:
        json.dump(info, f, indent=2)
    logging.info("Wrote metadata to %s", FLAG_INFO_PATH)
    repo = os.path.join(BASE_DIR, "github-pages")
    # ensure Git author identity for commits
    subprocess.run(["git", "-C", repo, "config", "user.name", "Christopher Hærem"], check=True)
    subprocess.run(["git", "-C", repo, "config", "user.email", "chris.haerem@gmail.com"], check=True)
    subprocess.run(["git", "-C", repo, "add", "data/flag.json"], check=True)
    subprocess.run(["git", "-C", repo, "commit", "-m", f"Update flag: {info['country']}"], check=True)
    subprocess.run(["git", "-C", repo, "push"], check=True)
    logging.info("Pushed flag metadata to GitHub Pages")

def display_flag(epd, country_name=None):
    logging.info("Displaying flag...")

    # Get the list of countries
    data = get_country_data()

    country = None

    if country_name:
        country = get_country_by_name(data, country_name)
        if not country:
            raise ValueError(f"Country '{country_name}' not recognized")

    # If country not found or not specified, select a random country
    if not country:
        random_index = random.randint(0, len(data) - 1)
        country = data[random_index]

    # Get the flag URL
    flag_url = country["flags"]["png"]

    # Download and open the flag image
    flag_image = get_flag(flag_url)

    # Resize the flag image to the display size
    resized_flag_image = flag_image.resize((epd.width, epd.height), Image.Resampling.LANCZOS)

    # Display the flag image
    epd.display(epd.getbuffer(resized_flag_image))

    # Update GitHub Pages metadata
    update_flag_metadata(country)

    logging.info(f"Displayed flag for {country['name']['common']}")

try:
    logging.info("epd7in3f Demo")

    # Get country name from command line argument if provided
    country_name = sys.argv[1] if len(sys.argv) > 1 else None

    # Validate country name before initializing the display
    if country_name:
        data = get_country_data()
        if not get_country_by_name(data, country_name):
            raise ValueError(f"Country '{country_name}' not recognized")

    epd = epd7in3f.EPD()
    logging.info("init and Clear")
    epd.init()
    epd.Clear()

    # Add other drawing functions here...

    # Display flag
    display_flag(epd, country_name)
    
    logging.info("Goto Sleep...")
    epd.sleep()
        
except IOError as e:
    logging.info(e)
    
except ValueError as e:
    logging.error(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd7in3f.epdconfig.module_exit()
    exit()
