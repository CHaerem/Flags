#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
import json
import sys

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

def prepare_country_data():
    """Process country_cache.json and save it to static/data for direct use by the frontend"""
    try:
        # File paths
        cache_path = os.path.join(project_root, "country_cache.json")
        static_data_dir = os.path.join(project_root, "app", "static", "data")
        output_path = os.path.join(static_data_dir, "countries.json")
        
        # Create the data directory if it doesn't exist
        os.makedirs(static_data_dir, exist_ok=True)
        
        # Load the country data
        with open(cache_path, 'r', encoding='utf-8') as f:
            countries = json.load(f)
            
        # Create a dictionary indexed by country name for faster lookups
        country_dict = {}
        for country in countries:
            if 'name' in country and 'common' in country['name']:
                country_name = country['name']['common']
                country_dict[country_name] = country
        
        # Save processed data to static directory
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(country_dict, f, ensure_ascii=False, indent=2)
            
        print(f"Country data prepared successfully and saved to {output_path}")
        print(f"Total countries processed: {len(country_dict)}")
        
    except Exception as e:
        print(f"Error preparing country data: {str(e)}")
        return False
        
    return True

if __name__ == "__main__":
    prepare_country_data()