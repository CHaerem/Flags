"""
E-Paper display driver implementation for Waveshare 7.3" e-paper display.
This module handles all direct interactions with the physical e-paper hardware.
"""

import os
import time
import logging
from PIL import Image

# Configure logging
logger = logging.getLogger(__name__)

class EPaperDisplay:
    """
    Driver for Waveshare 7.3" E-Paper Display.
    Handles initialization, display updates, and error recovery.
    """

    def __init__(self):
        """Initialize the e-paper display driver."""
        self._epd = None
        self.width = 800  # Default width
        self.height = 480  # Default height
        self.initialized = False
        self._initialize()

    def _initialize(self):
        """
        Initialize the display hardware.
        This is separated from __init__ to allow for retry logic.
        """
        try:
            # Import waveshare module dynamically to avoid import issues
            from waveshare_epd import epd7in3f
            self._epd = epd7in3f.EPD()
            self.width = self._epd.width
            self.height = self._epd.height
            logger.info("E-Paper display driver initialized")
            self.initialized = True
            return True
        except Exception as e:
            logger.error(f"Failed to initialize e-paper display: {e}")
            self.initialized = False
            return False

    def reset(self):
        """
        Reset the display hardware.
        Useful for recovering from errors.
        """
        if not self._epd:
            if not self._initialize():
                logger.error("Cannot reset display - not initialized")
                return False
                
        try:
            self._epd.reset()
            time.sleep(0.1)  # Short delay after reset
            logger.debug("Display reset complete")
            return True
        except Exception as e:
            logger.error(f"Error resetting display: {e}")
            self.initialized = False
            return False

    def init(self):
        """
        Initialize the display for updates.
        Must be called before displaying content.
        """
        if not self._epd:
            if not self._initialize():
                logger.error("Cannot initialize display - driver not available")
                return False
                
        try:
            self._epd.init()
            logger.debug("Display initialized for updates")
            return True
        except Exception as e:
            logger.error(f"Error initializing display for update: {e}")
            self.initialized = False
            return False

    def display_image(self, image, custom_width=None, custom_height=None):
        """
        Display an image on the e-paper display.
        
        Args:
            image (PIL.Image): The image to display. Will be resized to fit the display.
            custom_width (int, optional): Custom display width to override the default.
            custom_height (int, optional): Custom display height to override the default.
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self._epd:
            if not self._initialize():
                logger.error("Cannot update display - not initialized")
                return False
                
        try:
            # Ensure display is initialized
            if not self.init():
                return False
                
            # Use custom dimensions if provided, otherwise use hardware defaults
            target_width = custom_width if custom_width is not None else self.width
            target_height = custom_height if custom_height is not None else self.height
                
            # Resize image if needed
            if image.size != (target_width, target_height):
                image = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
                
            # Display the image
            self._epd.display(self._epd.getbuffer(image))
            logger.info(f"Image displayed successfully at size: {target_width}x{target_height}")
            return True
        except Exception as e:
            logger.error(f"Error displaying image: {e}")
            # Try to reset the display on error
            try:
                self.reset()
            except:
                pass
            return False
            
    def sleep(self):
        """
        Put the display to sleep to save power.
        Should be called after updates are complete.
        """
        if not self._epd:
            return False
            
        try:
            # Try to re-initialize if needed before sleeping
            if not self.initialized:
                self._initialize()
                
            self._epd.sleep()
            logger.debug("Display put to sleep")
            return True
        except Exception as e:
            logger.error(f"Error putting display to sleep: {e}")
            # Try to reset the hardware connection
            try:
                from waveshare_epd import epd7in3f
                epd7in3f.epdconfig.module_exit()
                time.sleep(0.5)  # Give hardware time to reset
                self._initialize()  # Attempt to re-initialize
                return True  # Return success even if sleep failed but we recovered
            except Exception as reinit_error:
                logger.error(f"Failed to reset display hardware: {reinit_error}")
                self.initialized = False
                self._epd = None
                return False
            
    def close(self):
        """
        Close the display and free resources.
        Should be called when done with the display.
        """
        try:
            if self._epd:
                self.sleep()
                self._epd = None
                self.initialized = False
            return True
        except Exception as e:
            logger.error(f"Error closing display: {e}")
            self._epd = None
            self.initialized = False
            return False
            
    def __enter__(self):
        """Context manager entry."""
        self.init()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()