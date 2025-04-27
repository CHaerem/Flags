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

# Import configuration
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config_manager import load_config

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to import main with required functions
try:
    # Only import display_flag function to avoid triggering GPIO initialization
    from main import update_flag_metadata, get_country_by_name, get_country_data, get_flag
    FLAG_FUNCTIONS_AVAILABLE = True
except Exception as e:
    logger.error(f"Error importing flag functions: {e}")
    FLAG_FUNCTIONS_AVAILABLE = False

# Import display manager
try:
    from display import get_display_manager, DISPLAY_AVAILABLE
except Exception as e:
    logger.error(f"Error importing display module: {e}")
    DISPLAY_AVAILABLE = False

def update_flag_safely(country_name=None, force_cleanup=False):
    """
    Update flag with proper display handling.
    
    Args:
        country_name (str, optional): The name of the country whose flag to display.
                                     If None, a random country is chosen.
        force_cleanup (bool, optional): Whether to force clean up any stale locks.
        
    Returns:
        int: 0 for success, non-zero for error.
    """
    # Load configuration
    config = load_config()
    display_config = config.get('flag_display', {})
    
    # Check if we should use fixed country from configuration
    # When no specific country is requested and mode is set to fixed
    if country_name is None and display_config.get('mode') == 'fixed':
        fixed_country = display_config.get('fixed_country')
        if fixed_country:
            logger.info(f"Using fixed country from configuration: {fixed_country}")
            country_name = fixed_country
    
    # Get display manager with current config
    display_manager = get_display_manager(display_config)
    
    # If flag functions aren't available, we can't update anything
    if not FLAG_FUNCTIONS_AVAILABLE:
        logger.error("Required flag functions not available")
        return 1
    
    # Get country data
    try:
        # Load country data
        data = get_country_data()
        
        # Get specified country or random country
        country = get_country_by_name(data, country_name) if country_name else None
        
        # If specified country not found or none specified, choose random country
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
        
        # If display is not available, just return success after updating metadata
        if not DISPLAY_AVAILABLE or not display_manager.is_display_available():
            logger.info("Physical display not available - metadata updated only")
            return 0
    except Exception as e:
        logger.error(f"Error preparing flag data: {e}")
        logger.debug(traceback.format_exc())
        return 1
    
    # Try to update the physical display
    try:
        # Display the flag image
        success = display_manager.display_image(flag_img)
        
        if success:
            logger.info(f"Displayed flag for {country['name']['common']}")
            return 0
        else:
            logger.warning("Flag metadata updated but physical display update failed")
            return 0  # Still return success since metadata was updated
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