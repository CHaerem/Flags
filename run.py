#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
import sys
import logging
from apscheduler.schedulers.background import BackgroundScheduler

# Add scripts directory to path so we can import from it
current_dir = os.path.dirname(os.path.abspath(__file__))
scripts_dir = os.path.join(current_dir, "scripts")
sys.path.append(scripts_dir)

# Import the prepare_country_data function
from prepare_country_data import prepare_country_data
from app import create_app
# Import configuration manager
from scripts.config_manager import load_config, get_flag_display_settings
# Import the display lock
from scripts.display_lock import DisplayLock

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create the Flask application
app = create_app()

# Load configuration
config = load_config()
flag_settings = get_flag_display_settings()

# Try to import the display module, but handle the case when it's not available
try:
    # Import the flag display functionality
    from scripts.main import display_flag, epd7in3f
    EPD_AVAILABLE = True
    logger.info("E-paper display module loaded successfully")
except (ImportError, RuntimeError, ModuleNotFoundError) as e:
    logger.warning(f"E-paper display module not available: {e}")
    EPD_AVAILABLE = False
    # Import just the display_flag function (which will work in headless mode)
    from scripts.main import display_flag

def update_flag_display():
    """Function to update the e-ink flag display"""
    # Check if flag display is enabled in config
    settings = get_flag_display_settings()
    if not settings.get('enabled', True):
        logger.info("Flag display updates are disabled in config")
        return

    try:
        logger.info("Scheduled flag update starting...")
        
        # Check if we should run in headless mode
        headless_mode = settings.get('headless', False)
        
        if headless_mode or not EPD_AVAILABLE:
            logger.info("Running in headless mode (no physical display updates)")
            # In headless mode, we just update the flag metadata
            display_flag(None)
        else:
            # With physical display available, use a lock to prevent concurrent access
            with DisplayLock() as lock:
                if not lock.acquired:
                    logger.warning("Could not acquire display lock, running in headless mode")
                    display_flag(None)
                    return
                    
                try:
                    epd = epd7in3f.EPD()
                    epd.init()
                    display_flag(epd)
                    epd.sleep()
                except Exception as e:
                    logger.error(f"Display hardware error: {e}")
                    # Fall back to headless mode if hardware access fails
                    logger.info("Falling back to headless mode")
                    display_flag(None)
        
        logger.info("Scheduled flag update completed")
    except Exception as e:
        logger.error(f"Error updating flag display: {e}", exc_info=True)

# Initialize the scheduler
scheduler = BackgroundScheduler()

if __name__ == "__main__":
    # Prepare country data at startup
    print("Preparing country data...")
    if prepare_country_data():
        print("Country data prepared successfully!")
    else:
        print("Warning: Failed to prepare country data")
    
    # Set up the scheduler based on configuration
    update_interval = flag_settings.get('update_interval_minutes', 30)
    
    if flag_settings.get('enabled', True):
        # Add scheduled job with interval from config
        scheduler.add_job(update_flag_display, 'interval', minutes=update_interval)
        
        # Also update the flag display at startup if configured
        if flag_settings.get('update_at_startup', True):
            scheduler.add_job(update_flag_display)
            
        # Start the scheduler
        scheduler.start()
        
        # Log whether we're in headless mode
        if flag_settings.get('headless', False) or not EPD_AVAILABLE:
            print(f"Flag display running in HEADLESS mode - updates scheduled every {update_interval} minutes")
        else:
            print(f"Flag display updates enabled - will update every {update_interval} minutes")
    else:
        print("Flag display updates are disabled in config")
    
    print(f"Starting server at http://0.0.0.0:5000/")
    print(f"Access locally via http://smartpi.local:5000/")
    print("CTRL+C to stop the server")
    
    try:
        # Start Flask without HTTPS
        app.run(host="0.0.0.0", port=5000)
    except (KeyboardInterrupt, SystemExit):
        # Ensure clean shutdown of scheduler when app terminates
        scheduler.shutdown()