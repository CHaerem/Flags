#!/usr/bin/python
# -*- coding:utf-8 -*-

import sys
import os
import logging
import traceback
import time

# Configure logging before any imports that might use it
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import configuration and display lock first
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config_manager import load_config

# Import display lock
try:
    from display_lock import DisplayLock
except Exception as e:
    logger.error(f"Failed to import DisplayLock: {e}")
    sys.exit(1)

# Try to import main with display_flag function
try:
    # Only import display_flag function to avoid triggering GPIO initialization
    from main import display_flag, update_flag_metadata, get_country_by_name, get_country_data, get_flag
    EPD_AVAILABLE = True
except Exception as e:
    logger.error(f"Error importing flag display modules: {e}")
    EPD_AVAILABLE = False

# Try to import waveshare module separately
try:
    from waveshare_epd import epd7in3f
    EPD_MODULE_AVAILABLE = True
except Exception as e:
    logger.error(f"Error importing waveshare module: {e}")
    EPD_MODULE_AVAILABLE = False

def update_flag_safely(country_name=None):
    """Update flag with proper display lock handling"""
    config = load_config()
    headless_mode = config.get('flag_display', {}).get('headless', False)
    
    # If we can't import the required modules, run in headless mode
    if not EPD_AVAILABLE:
        logger.warning("Running in headless mode - required modules not available")
        headless_mode = True
    
    # Get country data
    try:
        data = get_country_data()
        country = get_country_by_name(data, country_name) if country_name else None
        if country_name and not country:
            logger.warning(f"Country '{country_name}' not recognized, using random country instead")
            import random
            random_key = random.choice(list(data.keys()))
            country = data[random_key]
        elif not country_name:
            import random
            random_key = random.choice(list(data.keys()))
            country = data[random_key]
            
        # Get flag image
        flag_img = get_flag(country)
        
        # Update metadata regardless of display availability
        update_flag_metadata(country)
        logger.info(f"Updated metadata for {country['name']['common']}")
        
        # If in headless mode, just return after updating metadata
        if headless_mode or not EPD_MODULE_AVAILABLE:
            logger.info("Running in headless mode - not updating physical display")
            return 0
    except Exception as e:
        logger.error(f"Error preparing flag data: {e}")
        logger.debug(traceback.format_exc())
        return 1
        
    # Try to update the physical display with proper locking
    try:
        # First try to acquire the display lock
        with DisplayLock(timeout=15) as lock:
            if not lock.acquired:
                logger.warning("Could not acquire display lock, skipping physical display update")
                return 0
                
            try:
                # Wait a moment before initializing display (helps prevent GPIO conflicts)
                time.sleep(0.5)
                
                # Initialize the display
                epd = epd7in3f.EPD()
                logger.info("Display initialized successfully")
                epd.init()
                
                # Resize image to display dimensions
                display_width = config.get('display', {}).get('width', epd.width)
                display_height = config.get('display', {}).get('height', epd.height)
                from PIL import Image
                resized = flag_img.resize((display_width, display_height), Image.Resampling.LANCZOS)
                
                # Display the flag
                epd.display(epd.getbuffer(resized))
                logger.info(f"Displayed flag for {country['name']['common']}")
                
                # Sleep the display
                epd.sleep()
                logger.info("Display update completed successfully")
                return 0
            except Exception as e:
                logger.error(f"Display error: {e}")
                logger.debug(traceback.format_exc())
                return 1
    except Exception as e:
        logger.error(f"Error updating flag: {e}")
        logger.debug(traceback.format_exc())
        return 1

if __name__ == "__main__":
    try:
        country_arg = sys.argv[1] if len(sys.argv) > 1 else None
        exit_code = update_flag_safely(country_arg)
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"Unhandled error: {e}")
        logger.debug(traceback.format_exc())
        sys.exit(1)