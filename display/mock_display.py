"""
Mock display driver implementation for development testing.
This module simulates the e-paper display and provides a web preview interface.
"""

import os
import time
import logging
import threading
from PIL import Image
import base64
from io import BytesIO

from .interfaces import DisplayInterface

# Configure logging
logger = logging.getLogger(__name__)

# Global variable to store the latest displayed image
current_display_image = None
display_image_lock = threading.Lock()

class MockDisplay(DisplayInterface):
    """
    Mock implementation of e-paper display for development testing.
    Provides a web preview of what would appear on the physical display.
    """

    def __init__(self):
        """Initialize the mock display driver."""
        self.width = 800  # Default width
        self.height = 480  # Default height
        self.initialized = True
        logger.info("Mock display initialized")

    def init(self):
        """Initialize the display for updates."""
        logger.debug("Mock display ready for updates")
        self.initialized = True
        return True
        
    def display_image(self, image, custom_width=None, custom_height=None):
        """
        Store the image for web preview display.
        
        Args:
            image (PIL.Image): The image to display. Will be resized to fit the display.
            custom_width (int, optional): Custom display width to override the default.
            custom_height (int, optional): Custom display height to override the default.
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Use custom dimensions if provided, otherwise use hardware defaults
            target_width = custom_width if custom_width is not None else self.width
            target_height = custom_height if custom_height is not None else self.height
                
            # Resize image if needed
            if image.size != (target_width, target_height):
                image = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
            
            # Store the image in the global variable for web preview
            global current_display_image
            with display_image_lock:
                current_display_image = image.copy()
                
            logger.info(f"Image successfully stored for mock display at size: {target_width}x{target_height}")
            return True
        except Exception as e:
            logger.error(f"Error displaying mock image: {e}")
            return False
        
    def sleep(self):
        """Put the display to sleep to save power (mock implementation)."""
        logger.debug("Mock display put to sleep")
        return True
        
    def close(self):
        """Close the display and free resources."""
        logger.debug("Mock display closed")
        self.initialized = False
        return True

    @staticmethod
    def get_current_image_base64():
        """
        Get the current display image as a base64 encoded string.
        
        Returns:
            str: Base64 encoded image or None if no image is available
        """
        global current_display_image
        with display_image_lock:
            if current_display_image is None:
                return None
                
            buffered = BytesIO()
            current_display_image.save(buffered, format="PNG")
            return base64.b64encode(buffered.getvalue()).decode('utf-8')