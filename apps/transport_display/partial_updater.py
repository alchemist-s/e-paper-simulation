#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
Partial update system for transport display
Handles updating only the time display without refreshing the entire screen
"""

from typing import Tuple, Optional
from PIL import Image, ImageDraw
import logging

from .models import DisplayConfig, JourneyStop
from .font_manager import FontManager

logger = logging.getLogger(__name__)


class PartialUpdater:
    """Handles partial updates for time display"""

    def __init__(self, config: DisplayConfig):
        self.config = config
        self.font_manager = FontManager(config)

        # Define regions for partial updates
        self.banner_time_region = self._calculate_banner_time_region()
        self.next_service_time_region = self._calculate_next_service_time_region()

    def _calculate_banner_time_region(self) -> Tuple[int, int, int, int]:
        """Calculate the region for banner time display"""
        banner_font = self.font_manager.get_font("arial", self.config.banner_font_size)

        # Calculate time text dimensions
        time_label = "Time now: 23:59"  # Use max expected width
        bbox = banner_font.getbbox(time_label)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Calculate position (right-aligned in banner)
        x = self.config.width - text_width - self.config.content_padding
        y = (self.config.banner_height - text_height) // 2

        # Add padding around the region
        padding = 5
        return (
            x - padding,
            y - padding,
            x + text_width + padding,
            y + text_height + padding,
        )

    def _calculate_next_service_time_region(self) -> Tuple[int, int, int, int]:
        """Calculate the region for next service time display"""
        time_font = self.font_manager.get_font("arial_bold", self.config.time_font_size)

        # Calculate time text dimensions (use max expected width)
        time_text = "99 min"  # Max expected width
        bbox = time_font.getbbox(time_text)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Calculate position (bottom right)
        x = self.config.width - text_width - 40
        y = self.config.height - text_height - 40

        # Add padding around the region
        padding = 10
        return (
            x - padding,
            y - padding,
            x + text_width + padding,
            y + text_height + padding,
        )

    def create_banner_time_update(
        self, current_time: str
    ) -> Tuple[Image.Image, Tuple[int, int, int, int]]:
        """Create a partial update image for the banner time"""
        # Create image for the time region
        region_width = self.banner_time_region[2] - self.banner_time_region[0]
        region_height = self.banner_time_region[3] - self.banner_time_region[1]

        image = Image.new("1", (region_width, region_height), 0)  # Black background
        draw = ImageDraw.Draw(image)

        # Draw the time text
        banner_font = self.font_manager.get_font("arial", self.config.banner_font_size)
        time_label = f"Time now: {current_time}"

        # Center text in the region
        bbox = draw.textbbox((0, 0), time_label, font=banner_font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (region_width - text_width) // 2
        y = (region_height - text_height) // 2

        draw.text((x, y), time_label, font=banner_font, fill=255)  # White text

        return image, self.banner_time_region

    def create_next_service_time_update(
        self, next_stop: JourneyStop
    ) -> Tuple[Image.Image, Tuple[int, int, int, int]]:
        """Create a partial update image for the next service time"""
        # Create image for the time region
        region_width = (
            self.next_service_time_region[2] - self.next_service_time_region[0]
        )
        region_height = (
            self.next_service_time_region[3] - self.next_service_time_region[1]
        )

        image = Image.new("1", (region_width, region_height), 255)  # White background
        draw = ImageDraw.Draw(image)

        # Draw the time text
        time_font = self.font_manager.get_font("arial_bold", self.config.time_font_size)
        time_text = next_stop.time_display

        # Center text in the region
        bbox = draw.textbbox((0, 0), time_text, font=time_font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (region_width - text_width) // 2
        y = (region_height - text_height) // 2

        draw.text((x, y), time_text, font=time_font, fill=0)  # Black text

        return image, self.next_service_time_region

    def get_buffer_for_partial(self, image: Image.Image) -> bytes:
        """Convert image to buffer format for display_Partial"""
        # Convert to 1-bit and get raw bytes
        img_1bit = image.convert("1")
        buf = bytearray(img_1bit.tobytes("raw"))

        # Invert bytes (same as getbuffer in epd7in5b_V2)
        for i in range(len(buf)):
            buf[i] ^= 0xFF

        return bytes(buf)
