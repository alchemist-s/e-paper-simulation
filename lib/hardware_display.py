from display_interface import DisplayInterface
from PIL import Image


class HardwareDisplay(DisplayInterface):
    """Hardware implementation for actual e-ink display"""

    def __init__(self, epd_module):
        self.epd = epd_module()

    def init(self):
        """Initialize the display"""
        return self.epd.init()

    def clear(self):
        """Clear the display"""
        self.epd.Clear()

    def display(self, main_image: Image.Image, other_image: Image.Image = None):
        """Display images on the screen"""
        if other_image:
            # Both images provided
            self.epd.display(
                self.epd.getbuffer(main_image), self.epd.getbuffer(other_image)
            )
        else:
            # Only main image provided, create blank red image
            blank_red = Image.new("1", (self.epd.width, self.epd.height), 255)
            self.epd.display(
                self.epd.getbuffer(main_image), self.epd.getbuffer(blank_red)
            )

    def init_fast(self):
        """Initialize for fast mode"""
        self.epd.init_Fast()

    def sleep(self):
        """Put display to sleep"""
        self.epd.sleep()

    @property
    def width(self) -> int:
        """Display width in pixels"""
        return self.epd.width

    @property
    def height(self) -> int:
        """Display height in pixels"""
        return self.epd.height
