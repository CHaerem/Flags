"""
Display module for the Flag API.
This package contains all functionality related to physical display operations.
"""

import os
import logging
import sys

# Configure logging for the display module
logger = logging.getLogger(__name__)

# Check if display hardware is available
try:
    from .epaper import EPaperDisplay
    DISPLAY_AVAILABLE = True
except ImportError as e:
    logger.warning(f"EPaper display module not available: {e}")
    DISPLAY_AVAILABLE = False

# Import the display manager for general use
from .manager import DisplayManager, get_display_manager

__all__ = ['DisplayManager', 'get_display_manager', 'DISPLAY_AVAILABLE']