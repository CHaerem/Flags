"""
Display Manager for the Flag API.
Provides a centralized interface for all display operations.
"""

import os
import time
import logging
import threading
from PIL import Image

from .lock import DisplayLock
from .interfaces import DisplayInterface

# Configure logging
logger = logging.getLogger(__name__)

# Singleton instance
_display_manager_instance = None

def get_display_manager(config=None):
    """
    Get the singleton instance of the DisplayManager.
    
    Args:
        config (dict, optional): Configuration dictionary for the display manager.
        
    Returns:
        DisplayManager: The singleton display manager instance.
    """
    global _display_manager_instance
    if _display_manager_instance is None:
        _display_manager_instance = DisplayManager(config)
    elif config is not None:
        _display_manager_instance.update_config(config)
    return _display_manager_instance

class DisplayManager:
    """
    Central manager for display operations.
    Handles display initialization, updates, and provides fallbacks when hardware is unavailable.
    """
    
    def __init__(self, config=None):
        """
        Initialize the display manager.
        
        Args:
            config (dict, optional): Configuration dictionary for the display manager.
        """
        self.config = config or {}
        self.headless = self.config.get('headless', False)
        self._display = None
        self._display_type = None
        self._lock = threading.Lock()
        
        # Try to initialize the display based on configuration
        self._initialize_display()
        
    def _initialize_display(self):
        """Initialize the appropriate display based on configuration."""
        # Don't initialize if we're in headless mode
        if self.headless:
            logger.info("Running in headless mode - no physical display will be used")
            return False
            
        # Try to load the display interface
        try:
            # Default to e-paper display
            from .epaper import EPaperDisplay
            self._display = EPaperDisplay()
            self._display_type = "epaper"
            logger.info("E-Paper display initialized successfully")
            return True
        except ImportError:
            logger.warning("E-Paper display module not available")
            
        # No display available, fall back to headless mode
        self.headless = True
        logger.warning("No display drivers available - falling back to headless mode")
        return False
        
    def update_config(self, config):
        """
        Update the display manager configuration.
        
        Args:
            config (dict): New configuration dictionary.
        """
        if not config:
            return
            
        self.config.update(config)
        # Check if headless mode changed
        new_headless = self.config.get('headless', self.headless)
        
        if new_headless != self.headless:
            self.headless = new_headless
            if not self.headless and self._display is None:
                # We were in headless mode but now we want a display
                self._initialize_display()
            elif self.headless and self._display is not None:
                # We had a display but now want headless mode
                self.close_display()
                self._display = None
    
    def is_display_available(self):
        """
        Check if a physical display is available and initialized.
        
        Returns:
            bool: True if a display is available, False otherwise.
        """
        return self._display is not None and getattr(self._display, 'initialized', False)
    
    def display_image(self, image, force_update=False):
        """
        Display an image on the physical display if available.
        
        Args:
            image (PIL.Image): The image to display.
            force_update (bool, optional): Force update even in headless mode. Defaults to False.
            
        Returns:
            bool: True if display was updated, False otherwise.
        """
        if self.headless and not force_update:
            logger.info("Skipping physical display update (headless mode)")
            return False
            
        if not self._display:
            if not force_update:
                return False
            # Try to initialize the display again if forced
            if not self._initialize_display():
                return False
        
        # Use a thread lock to prevent concurrent access from the same process
        with self._lock:
            # Use a file lock to prevent concurrent access from different processes
            with DisplayLock() as lock:
                if not lock.acquired:
                    logger.warning("Could not acquire display lock, skipping update")
                    return False
                
                try:
                    result = self._display.display_image(image)
                    self._display.sleep()
                    return result
                except Exception as e:
                    logger.error(f"Error updating display: {e}")
                    return False
    
    def close_display(self):
        """Close the display and free resources."""
        if self._display:
            try:
                self._display.close()
                logger.debug("Display closed")
                return True
            except Exception as e:
                logger.error(f"Error closing display: {e}")
                return False
        return True
    
    def __del__(self):
        """Destructor to ensure display is properly closed."""
        self.close_display()