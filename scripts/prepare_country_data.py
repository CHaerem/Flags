#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
import json
import sys
import requests
from datetime import datetime
import time

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

def prepare_country_data():
    """Fetch country data from REST Countries API and prepare it for the frontend"""
    try:
        # File paths
        cache_path = os.path.join(project_root, "country_cache.json")
        static_data_dir = os.path.join(project_root, "app", "static", "data")
        output_path = os.path.join(static_data_dir, "countries.json")
        flag_output_path = os.path.join(static_data_dir, "flag.json")
        
        # Create the data directory if it doesn't exist
        os.makedirs(static_data_dir, exist_ok=True)
        
        # Load existing data if available
        existing_data = {}
        if os.path.exists(output_path):
            try:
                with open(output_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                print(f"Loaded {len(existing_data)} existing countries from {output_path}")
            except json.JSONDecodeError:
                print(f"Warning: Could not parse existing data at {output_path}, starting fresh")
        
        # Try to fetch fresh data from REST Countries API with retry logic
        api_data = None
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                print(f"Fetching country data from REST Countries API (attempt {attempt+1}/{max_retries})...")
                api_url = "https://restcountries.com/v3.1/all"
                response = requests.get(api_url, timeout=10)  # Add timeout
                response.raise_for_status()
                api_data = response.json()
                break
            except requests.RequestException as e:
                if attempt < max_retries - 1:
                    print(f"Attempt {attempt+1} failed: {str(e)}. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    print(f"All {max_retries} attempts failed. Last error: {str(e)}")
        
        # If API failed, try to use cached data
        if api_data is None:
            if os.path.exists(cache_path):
                print(f"Using cached data from {cache_path} as fallback...")
                try:
                    with open(cache_path, 'r', encoding='utf-8') as f:
                        api_data = json.load(f)
                    print(f"Successfully loaded {len(api_data)} countries from cache")
                except Exception as e:
                    print(f"Error loading cache file: {str(e)}")
        
        # If we still don't have data, use a fallback URL
        if api_data is None:
            try:
                print("Trying alternative API endpoints...")
                # Try an alternative URL
                alt_url = "https://raw.githubusercontent.com/mledoze/countries/master/countries.json"
                response = requests.get(alt_url, timeout=10)
                response.raise_for_status()
                api_data = response.json()
                print(f"Successfully fetched data from alternative source")
            except Exception as e:
                print(f"Alternative source failed too: {str(e)}")
                return False
        
        # Process API data into our desired format
        country_dict = {}
        for country in api_data:
            # Handle differences in data structure between different sources
            if isinstance(country.get("name"), dict) and "common" in country["name"]:
                # Standard REST Countries API format
                country_name = country["name"]["common"]
            elif isinstance(country.get("name"), dict) and "official" in country["name"]:
                # Handle different formats
                country_name = country["name"]["official"]
            elif "name" in country and isinstance(country["name"], str):
                # Alternative format
                country_name = country["name"]
            else:
                # Skip entries without a name
                continue
                
            # Create or update country entry
            country_entry = existing_data.get(country_name, {})
            
            # Update basic fields, handling different data structures
            country_entry["name"] = country.get("name", {})
            country_entry["flag"] = country.get("flag", "")
            country_entry["flags"] = country.get("flags", {})
            country_entry["capital"] = country.get("capital", [])
            country_entry["region"] = country.get("region", "")
            country_entry["subregion"] = country.get("subregion", "")
            country_entry["population"] = country.get("population", 0)
            country_entry["languages"] = country.get("languages", {})
            country_entry["currencies"] = country.get("currencies", {})
            country_entry["timezones"] = country.get("timezones", [])
            country_entry["cca2"] = country.get("cca2", country.get("alpha2Code", ""))
            country_entry["cca3"] = country.get("cca3", country.get("alpha3Code", ""))
            
            # Store in our dictionary
            country_dict[country_name] = country_entry
        
        # Save both the complete data as a cache and the processed data
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(api_data, f, ensure_ascii=False, indent=2)
            print(f"Saved raw data to cache file: {cache_path}")
            
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(country_dict, f, ensure_ascii=False, indent=2)
            print(f"Saved processed country data to: {output_path}")
            
        # Create a default flag.json if it doesn't exist (for initial load)
        if not os.path.exists(flag_output_path):
            # Use Norway as default if available, otherwise first country
            country_name = 'Norway' if 'Norway' in country_dict else next(iter(country_dict))
            default_country = country_dict[country_name]
            
            default_flag = {
                'country': country_name,
                'info': f"Capital: {default_country['capital'][0] if default_country['capital'] else '-'}",
                'emoji': default_country['flag'],
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            with open(flag_output_path, 'w', encoding='utf-8') as f:
                json.dump(default_flag, f, ensure_ascii=False, indent=2)
            
        print(f"Country data prepared successfully!")
        print(f"Total countries processed: {len(country_dict)}")
        
    except Exception as e:
        print(f"Unexpected error preparing country data: {str(e)}")
        return False
        
    return True

if __name__ == "__main__":
    prepare_country_data()