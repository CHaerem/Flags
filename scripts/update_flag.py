#!/usr/bin/python
# -*- coding:utf-8 -*-

import sys
import os
import logging
import traceback
from display_lock import DisplayLock
from main import display_flag
from waveshare_epd import epd7in3f
from config_manager import load_config

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def update_flag_safely(country_name=None):
    """Update flag with proper display lock handling"""
    config = load_config()
    headless_mode = config.get('flag_display', {}).get('headless', False)
    
    try:
        # First try to acquire the display lock
        with DisplayLock(timeout=15) as lock:
            if not lock.acquired:
                logger.warning("Could not acquire display lock, running in headless mode")
                return display_flag(None, country_name)
                
            try:
                # Initialize the display
                epd = epd7in3f.EPD()
                epd.init()
                
                # Display the flag
                country = display_flag(epd, country_name)
                
                # Sleep the display
                epd.sleep()
                
                return country
            except Exception as e:
                logger.error(f"Display error: {e}")
                logger.debug(traceback.format_exc())
                # If there's an error with the display, fall back to headless mode
                return display_flag(None, country_name)
    except Exception as e:
        logger.error(f"Error updating flag: {e}")
        logger.debug(traceback.format_exc())
        # Fall back to headless mode if there's any error
        return display_flag(None, country_name)

if __name__ == "__main__":
    try:
        country_arg = sys.argv[1] if len(sys.argv) > 1 else None
        update_flag_safely(country_arg)
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unhandled error: {e}")
        logger.debug(traceback.format_exc())
        sys.exit(1)