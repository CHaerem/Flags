"""
Display interfaces for the Flag API.
Defines abstract base classes for display implementations.
"""

from abc import ABC, abstractmethod

class DisplayInterface(ABC):
    """Abstract base class for display implementations."""
    
    @abstractmethod
    def init(self):
        """Initialize the display for updates."""
        pass
        
    @abstractmethod
    def display_image(self, image):
        """
        Display an image on the display.
        
        Args:
            image: The image to display.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        pass
        
    @abstractmethod
    def sleep(self):
        """Put the display to sleep to save power."""
        pass
        
    @abstractmethod
    def close(self):
        """Close the display and free resources."""
        pass