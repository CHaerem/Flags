#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import logging
import datetime
import time
import argparse
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from flask import Flask

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the current directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import required modules
from app import create_app
from scripts.config_manager import load_config
from scripts.prepare_country_data import prepare_country_data
from scripts.update_flag import update_flag_safely

# Import display manager
try:
    from display import get_display_manager, DISPLAY_AVAILABLE
except ImportError as e:
    logger.warning(f"Display module not available: {e}")
    DISPLAY_AVAILABLE = False

# Parse command-line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description='Flag Display Web Application')
    parser.add_argument('--mock', action='store_true', help='Enable mock display mode for development')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode (no display updates)')
    parser.add_argument('--port', type=int, default=None, help='Port to run the server on (overrides config)')
    return parser.parse_args()

def get_flag_display_settings():
    """Load flag display settings from config."""
    config = load_config()
    return config.get('flag_display', {})

def update_flag_display():
    """Function to update the e-ink flag display"""
    # Check if flag display is enabled in config
    settings = get_flag_display_settings()
    if not settings.get('enabled', True):
        logger.info("Flag display updates are disabled in config")
        return

    try:
        logger.info("Scheduled flag update starting...")
        
        # Update the flag without specifying a country (will use random)
        success = update_flag_safely(None)
        
        logger.info("Scheduled flag update completed")
    except Exception as e:
        logger.error(f"Error updating flag display: {e}", exc_info=True)

def setup_time_based_schedule(scheduler, settings):
    """Set up time-based scheduling for flag updates"""
    # Get configuration values
    time_interval = int(settings.get('time_interval', 30))
    start_hour = int(settings.get('start_hour', 0))
    start_minute = int(settings.get('start_minute', 0))
    
    # Generate the cron trigger expressions
    if time_interval < 60:
        # For intervals less than an hour, use minute-based cron
        # Calculate which minutes of each hour to run on
        minutes = []
        current = start_minute
        while current < 60:
            minutes.append(current)
            current += time_interval
        
        minute_expr = ','.join(map(str, minutes))
        logger.info(f"Time-based updates scheduled at minutes {minute_expr} of every hour")
        
        scheduler.add_job(
            func=update_flag_display,
            trigger=CronTrigger(minute=minute_expr),
            id='flag_update_job',
            name='Update flag display (time-based)',
            replace_existing=True
        )
    elif time_interval == 60:
        # For exactly 1 hour interval
        logger.info(f"Time-based updates scheduled every hour at :{start_minute:02d}")
        
        scheduler.add_job(
            func=update_flag_display,
            trigger=CronTrigger(minute=start_minute),
            id='flag_update_job',
            name='Update flag display (hourly)',
            replace_existing=True
        )
    else:
        # For intervals of multiple hours
        hours_interval = time_interval // 60
        hours = []
        current_hour = start_hour
        
        while current_hour < 24:
            hours.append(current_hour)
            current_hour += hours_interval
            if current_hour >= 24:
                break
        
        hour_expr = ','.join(map(str, hours))
        logger.info(f"Time-based updates scheduled at {hour_expr}:{start_minute:02d}")
        
        scheduler.add_job(
            func=update_flag_display,
            trigger=CronTrigger(hour=hour_expr, minute=start_minute),
            id='flag_update_job',
            name='Update flag display (time-based)',
            replace_existing=True
        )

def setup_scheduler(app):
    """Set up the background scheduler for periodic tasks."""
    scheduler = BackgroundScheduler()
    
    # Load display settings
    settings = get_flag_display_settings()
    
    # Add flag update job if enabled
    if settings.get('enabled', True):
        # Use time-based scheduling
        setup_time_based_schedule(scheduler, settings)
    else:
        logger.info("Flag display updates are disabled")

    # Start the scheduler
    scheduler.start()
    
    # Explicitly check if we should run an immediate update
    if settings.get('enabled', True) and settings.get('update_at_startup', True):
        time.sleep(1)  # Short delay to ensure app has started
        scheduler.add_job(
            func=update_flag_display,
            trigger='date',
            run_date=datetime.datetime.now() + datetime.timedelta(seconds=2),
            id='initial_flag_update')
    
    # Shut down the scheduler when the app terminates
    atexit.register(lambda: scheduler.shutdown())

if __name__ == '__main__':
    import atexit
    
    # Parse command-line arguments
    args = parse_arguments()
    
    # Prepare country data
    print("Preparing country data...")
    prepare_country_data()
    print("Country data prepared successfully!")
    
    # Initialize display manager with config
    config = load_config()
    display_config = config.get('flag_display', {})
    
    # Override config with command-line arguments
    if args.mock:
        print("Mock display mode enabled via command-line argument")
        display_config['use_mock'] = True
    else:
        # Ensure mock is disabled by default if not specified in command line
        display_config['use_mock'] = False
    
    if args.headless:
        print("Headless mode enabled via command-line argument")
        display_config['headless'] = True
    
    if DISPLAY_AVAILABLE:
        display_manager = get_display_manager(display_config)
        if display_manager.is_display_available():
            if display_manager.is_mock_display():
                print("Mock display initialized for development")
            else:
                print("E-Paper display initialized successfully")
        else:
            print("Running in headless mode - physical display not available")
    else:
        print("Display module not available - running in headless mode")
    
    # Create and configure the Flask app
    app = create_app()
    
    # Set up the scheduler
    setup_scheduler(app)
    
    # Get server configuration
    host = config.get('server', {}).get('host', '0.0.0.0')
    port = args.port if args.port is not None else config.get('server', {}).get('port', 5001)
    
    # Start the server
    print(f"Starting server at http://{host}:{port}/")
    if host == '0.0.0.0':
        print(f"Access locally via http://localhost:{port}/")
    print("CTRL+C to stop the server")
    app.run(host=host, port=port)