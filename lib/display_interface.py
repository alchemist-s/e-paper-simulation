from abc import ABC, abstractmethod
from PIL import Image


class DisplayInterface(ABC):
    """Abstract base class for display operations"""

    @abstractmethod
    def init(self):
        """Initialize the display"""
        pass

    @abstractmethod
    def clear(self):
        """Clear the display"""
        pass

    @abstractmethod
    def display(self, main_image: Image.Image, other_image: Image.Image = None):
        """Display images on the screen"""
        pass

    @abstractmethod
    def init_fast(self):
        """Initialize for fast mode (if supported)"""
        pass

    @abstractmethod
    def sleep(self):
        """Put display to sleep"""
        pass

    @property
    @abstractmethod
    def width(self) -> int:
        """Display width in pixels"""
        pass

    @property
    @abstractmethod
    def height(self) -> int:
        """Display height in pixels"""
        pass
