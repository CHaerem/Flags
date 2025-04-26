#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests
import json
from io import BytesIO
from PIL import Image

# Base directory of this project (~/Flags)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_FILE = os.path.join(BASE_DIR, "country_cache.json")
FLAG_CACHE_DIR = os.path.join(BASE_DIR, "flag_cache")

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return None

def save_flag_cache(flag_url, flag_image):
    if not os.path.exists(FLAG_CACHE_DIR):
        os.makedirs(FLAG_CACHE_DIR)
    flag_filename = os.path.join(FLAG_CACHE_DIR, os.path.basename(flag_url))
    flag_image.save(flag_filename)

def get_flag(flag_url):
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
        print(f"Downloaded and cached flag: {flag_url}")
    else:
        print(f"Error {response.status_code}: {response.reason}")

def download_all_flags():
    data = load_cache()
    if not data:
        response = requests.get("https://restcountries.com/v3.1/all?fields=name,flags")
        data = response.json()
        with open(CACHE_FILE, 'w') as f:
            json.dump(data, f)
        print("Fetched country data from API and saved to cache")

    for country in data:
        flag_url = country["flags"]["png"]
        get_flag(flag_url)

if __name__ == "__main__":
    download_all_flags()