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
        flag_output_path = os.path.join(static_data_dir, "flag.json")
        
        # Create the data directory if it doesn't exist
        os.makedirs(static_data_dir, exist_ok=True)
        
        # Load the country data
        with open(cache_path, 'r', encoding='utf-8') as f:
            countries = json.load(f)
            
        # Create dictionaries for different lookup methods
        country_dict = {}  # indexed by common name
        country_by_code = {}  # indexed by country code (cca2)
        
        for country in countries:
            if 'name' in country and 'common' in country['name']:
                country_name = country['name']['common']
                
                # Extract essential data fields
                country_data = {
                    'name': country['name'],
                    'flag': country.get('flag', ''),  # emoji flag
                    'flags': country.get('flags', {}),  # flag images
                    'capital': country.get('capital', []),
                    'region': country.get('region', ''),
                    'subregion': country.get('subregion', ''),
                    'population': country.get('population', 0),
                    'languages': country.get('languages', {}),
                    'currencies': country.get('currencies', {}),
                    'timezones': country.get('timezones', []),
                    'cca2': country.get('cca2', ''),
                    'cca3': country.get('cca3', ''),
                }
                
                # Add to dictionaries
                country_dict[country_name] = country_data
                
                # If country code is available, also index by it
                if 'cca2' in country:
                    country_by_code[country['cca2'].lower()] = country_data
        
        # Save processed data to static directory
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(country_dict, f, ensure_ascii=False, indent=2)
            
        # Create a default flag.json if it doesn't exist (for initial load)
        if not os.path.exists(flag_output_path):
            # Use Norway as default if available, otherwise first country
            default_country = country_dict.get('Norway', next(iter(country_dict.values())))
            default_flag = {
                'country': default_country['name']['common'],
                'flag': default_country['flag'],
                'updated': '',  # Will be filled by the display script
            }
            
            with open(flag_output_path, 'w', encoding='utf-8') as f:
                json.dump(default_flag, f, ensure_ascii=False, indent=2)
            
        print(f"Country data prepared successfully and saved to {output_path}")
        print(f"Total countries processed: {len(country_dict)}")
        
    except Exception as e:
        print(f"Error preparing country data: {str(e)}")
        return False
        
    return True

if __name__ == "__main__":
    prepare_country_data()