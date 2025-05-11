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
        self.use_mock = self.config.get('use_mock', False)
        self._display = None
        self._display_type = None
        self._lock = threading.Lock()
        
        # Try to initialize the display based on configuration
        self._initialize_display()
        
    def _initialize_display(self):
        """Initialize the appropriate display based on configuration."""
        # Don't initialize if we're in headless mode and not using mock
        if self.headless and not self.use_mock:
            logger.info("Running in headless mode - no physical display will be used")
            return False
        
        # Use mock display if specified in config
        if self.use_mock:
            try:
                from .mock_display import MockDisplay
                self._display = MockDisplay()
                self._display_type = "mock"
                logger.info("Mock display initialized for development testing")
                return True
            except ImportError as e:
                logger.warning(f"Mock display module not available: {e}")
        
        # Only try e-paper if not using mock and not in headless mode
        if not self.headless:
            # Try to load the e-paper display interface
            try:
                from .epaper import EPaperDisplay
                self._display = EPaperDisplay()
                self._display_type = "epaper"
                logger.info("E-Paper display initialized successfully")
                return True
            except ImportError as e:
                logger.warning(f"E-Paper display module not available: {e}")
            
        # No display available, fall back to headless mode
        if not self.use_mock:
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
        # Check if display mode changed
        new_headless = self.config.get('headless', self.headless)
        new_use_mock = self.config.get('use_mock', self.use_mock)
        
        if new_headless != self.headless or new_use_mock != self.use_mock:
            self.headless = new_headless
            self.use_mock = new_use_mock
            
            # Close any existing display
            if self._display is not None:
                self.close_display()
                self._display = None
                
            # Initialize with new settings
            self._initialize_display()
    
    def is_display_available(self):
        """
        Check if a physical display is available and initialized.
        
        Returns:
            bool: True if a display is available, False otherwise.
        """
        return self._display is not None and getattr(self._display, 'initialized', False)
    
    def get_display_type(self):
        """
        Get the type of display being used.
        
        Returns:
            str: Display type ("epaper", "mock", or None)
        """
        return self._display_type
        
    def is_mock_display(self):
        """
        Check if we're using a mock display.
        
        Returns:
            bool: True if using mock display
        """
        return self._display_type == "mock"
    
    def get_mock_display_image(self):
        """
        Get the current image from the mock display as base64 string.
        Only available when using mock display.
        
        Returns:
            str: Base64 encoded image or None
        """
        if not self.is_mock_display() or not self._display:
            return None
            
        try:
            return self._display.get_current_image_base64()
        except Exception as e:
            logger.error(f"Error getting mock display image: {e}")
            return None
    
    def display_image(self, image, force_update=False):
        """
        Display an image on the physical display if available.
        
        Args:
            image (PIL.Image): The image to display.
            force_update (bool, optional): Force update even in headless mode. Defaults to False.
            
        Returns:
            bool: True if display was updated, False otherwise.
        """
        # Special case for mock display - update even in headless mode
        if self.use_mock:
            if not self._display:
                self._initialize_display()
                
            if not self._display:
                return False
                
            # For mock display, we don't need locks or sleep
            custom_width = self.config.get('display', {}).get('width')
            custom_height = self.config.get('display', {}).get('height')
            
            try:
                return self._display.display_image(
                    image,
                    custom_width=custom_width,
                    custom_height=custom_height
                )
            except Exception as e:
                logger.error(f"Error updating mock display: {e}")
                return False
        
        # Normal display handling
        if self.headless and not force_update:
            logger.info("Skipping physical display update (headless mode)")
            return False
            
        if not self._display:
            if not force_update:
                return False
            # Try to initialize the display again if forced
            if not self._initialize_display():
                return False
        
        # Get custom width and height from config if available
        custom_width = self.config.get('display', {}).get('width')
        custom_height = self.config.get('display', {}).get('height')
        
        # Use a thread lock to prevent concurrent access from the same process
        with self._lock:
            # Use a file lock to prevent concurrent access from different processes
            with DisplayLock() as lock:
                if not lock.acquired:
                    logger.warning("Could not acquire display lock, skipping update")
                    return False
                
                try:
                    result = self._display.display_image(
                        image, 
                        custom_width=custom_width,
                        custom_height=custom_height
                    )
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