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

# Base directory of this script (~/Flags)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Paths (all inside your repo)
CACHE_FILE     = os.path.join(BASE_DIR, "country_cache.json")
FLAG_CACHE_DIR = os.path.join(BASE_DIR, "flag_cache")
FLAG_INFO_PATH = os.path.join(BASE_DIR, "docs", "data", "flag.json")


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

    url = "https://restcountries.com/v3.1/all?fields=name,flags,capital,flag"
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    save_cache(data)
    logging.info("Fetched country data and saved to cache")
    return data

def load_flag_cache(url):
    os.makedirs(FLAG_CACHE_DIR, exist_ok=True)
    fname = os.path.join(FLAG_CACHE_DIR, os.path.basename(url))
    if os.path.exists(fname):
        return Image.open(fname)
    return None

def save_flag_cache(url, img):
    os.makedirs(FLAG_CACHE_DIR, exist_ok=True)
    fname = os.path.join(FLAG_CACHE_DIR, os.path.basename(url))
    img.save(fname)

def get_flag(url):
    cached = load_flag_cache(url)
    if cached:
        logging.info("Loaded flag image from cache")
        return cached

    headers = {'User-Agent': 'Mozilla/5.0', 'Accept': 'image/png'}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    img = Image.open(BytesIO(resp.content))
    save_flag_cache(url, img)
    logging.info("Fetched flag image and saved to cache")
    return img

def get_country_by_name(data, name):
    for c in data:
        if c['name']['common'].lower() == name.lower():
            return c
    return None

def update_flag_metadata(country):
    # Build the metadata
    info = {
        "country": country['name']['common'],
        "info": f"Capital: {country.get('capital', ['Unknown'])[0]}",
        "emoji": country.get('flag', ''),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    # Ensure docs/data exists, then write JSON
    os.makedirs(os.path.dirname(FLAG_INFO_PATH), exist_ok=True)
    with open(FLAG_INFO_PATH, 'w') as f:
        json.dump(info, f, indent=2)
    logging.info("Wrote metadata to %s", FLAG_INFO_PATH)

    # Now commit & push from repo root
    repo = BASE_DIR
    subprocess.run([
        "sudo", "-u", "chris", "git", "-C", repo,
        "add", "docs/data/flag.json"
    ], check=True)
    subprocess.run([
        "sudo", "-u", "chris", "git", "-C", repo,
        "commit", "-m", f"Update flag: {info['country']}"
    ], check=True)
    subprocess.run([
        "sudo", "-u", "chris", "git", "-C", repo,
        "pull", "--rebase", "--autostash", "origin", "main"
    ], check=True)
    subprocess.run([
        "sudo", "-u", "chris", "git", "-C", repo,
        "push", "origin", "main"
    ], check=True)
    logging.info("Pushed flag metadata to GitHub Pages")

def display_flag(epd, country_name=None):
    logging.info("Displaying flag...")

    data = get_country_data()
    country = get_country_by_name(data, country_name) if country_name else None
    if country_name and not country:
        raise ValueError(f"Country '{country_name}' not recognized")
    if not country:
        country = random.choice(data)

    img = get_flag(country["flags"]["png"])
    
    # First update metadata and commit to GitHub
    update_flag_metadata(country)
    
    # Then display the flag on the e-paper display
    resized = img.resize((epd.width, epd.height), Image.Resampling.LANCZOS)
    epd.display(epd.getbuffer(resized))
    logging.info(f"Displayed flag for {country['name']['common']}")

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