from display_interface import DisplayInterface
from PIL import Image


class HardwareDisplay(DisplayInterface):
    """Hardware implementation for actual e-ink display"""

    def __init__(self, epd_module):
        self.epd = epd_module.EPD()

    def init(self):
        """Initialize the display"""
        self.epd.init()

    def clear(self):
        """Clear the display"""
        self.epd.Clear()

    def display(self, main_image: Image.Image, other_image: Image.Image = None):
        """Display images on the screen"""
        if other_image:
            self.epd.display(
                self.epd.getbuffer(main_image), self.epd.getbuffer(other_image)
            )
        else:
            self.epd.display(self.epd.getbuffer(main_image))

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
