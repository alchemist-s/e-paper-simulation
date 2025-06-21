#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import sys
import os
import time
import logging
from PIL import Image, ImageDraw, ImageFont

# Add the lib directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))

from waveshare_epd import epd7in5b_V2

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CounterDisplay:
    def __init__(self):
        """Initialize the e-paper display and counter"""
        self.epd = epd7in5b_V2.EPD()
        self.counter = 0
        self.font_size = 60
        self.text_color = 0  # Black
        self.bg_color = 255  # White

        # Text region tracking
        self.text_x = 50
        self.text_y = 200
        self.text_width = 700
        self.text_height = 80

        # Initialize the display for partial updates
        logger.info("Initializing e-paper display for partial updates...")
        if self.epd.init_part() != 0:
            logger.error("Failed to initialize e-paper display")
            sys.exit(1)

        # Clear the display initially
        self.epd.Clear()
        logger.info("Display initialized successfully")

        # Font setup
        try:
            font_options = [
                "/System/Library/Fonts/Arial.ttf",  # macOS
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
                "/usr/share/fonts/TTF/Arial.ttf",  # Some Linux distros
            ]

            self.font = None
            for font_path in font_options:
                if os.path.exists(font_path):
                    self.font = ImageFont.truetype(font_path, self.font_size)
                    break

            if self.font is None:
                self.font = ImageFont.load_default()
                logger.warning("Using default font - text may not display optimally")
        except Exception as e:
            logger.warning(f"Could not load system font: {e}")
            self.font = ImageFont.load_default()

    def create_text_image(self, text):
        """Create an image with the given text"""
        # Create full-size image for the display
        image = Image.new("1", (self.epd.width, self.epd.height), self.bg_color)
        draw = ImageDraw.Draw(image)

        # Get text bounding box
        bbox = draw.textbbox((0, 0), text, font=self.font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Center the text within the text region
        x = self.text_x + (self.text_width - text_width) // 2
        y = self.text_y + (self.text_height - text_height) // 2

        # Draw text
        draw.text((x, y), text, fill=self.text_color, font=self.font)

        return image

    def get_text_buffer(self, text):
        """Convert text image to buffer for display_Partial"""
        # Calculate buffer size based on display_Partial logic
        x_start = self.text_x
        x_end = self.text_x + self.text_width
        y_start = self.text_y
        y_end = self.text_y + self.text_height

        # Apply the same boundary adjustments as display_Partial
        if (
            (x_start % 8 + x_end % 8 == 8 & x_start % 8 > x_end % 8)
            | x_start % 8 + x_end % 8
            == 0 | (x_end - x_start) % 8
            == 0
        ):
            x_start = x_start // 8 * 8
            x_end = x_end // 8 * 8
        else:
            x_start = x_start // 8 * 8
            if x_end % 8 == 0:
                x_end = x_end // 8 * 8
            else:
                x_end = x_end // 8 * 8 + 1

        width_bytes = (x_end - x_start) // 8
        height = y_end - y_start

        # Create the text image for the region
        region_image = Image.new("1", (x_end - x_start, height), self.bg_color)
        draw = ImageDraw.Draw(region_image)

        # Get text bounding box
        bbox = draw.textbbox((0, 0), text, font=self.font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Center the text in the region
        text_x = (region_image.width - text_width) // 2
        text_y = (region_image.height - text_height) // 2

        # Draw text
        draw.text((text_x, text_y), text, fill=self.text_color, font=self.font)

        # Convert to buffer
        img = region_image.convert("1")
        buf = bytearray(img.tobytes("raw"))

        # Invert the bytes (same as getbuffer does)
        for i in range(len(buf)):
            buf[i] ^= 0xFF

        return buf

    def update_display(self, use_partial=True):
        """Update the display with the current counter value"""
        text = f"Counter {self.counter}"
        logger.info(f"Updating display: {text}")

        if use_partial and self.counter > 0:
            # Use partial display for updates after the first display
            buffer = self.get_text_buffer(text)

            # Calculate region coordinates
            x_start = self.text_x
            y_start = self.text_y
            x_end = self.text_x + self.text_width
            y_end = self.text_y + self.text_height

            # Update the specific region
            self.epd.display_Partial(buffer, x_start, y_start, x_end, y_end)
        else:
            # Full display for the first time
            image = self.create_text_image(text)
            buffer = self.epd.getbuffer(image)
            # Create a blank red buffer (no red content)
            red_buffer = [0x00] * (int(self.epd.width / 8) * self.epd.height)
            self.epd.display(buffer, red_buffer)

    def run(self, duration_seconds=None):
        """Run the counter display"""
        try:
            logger.info("Starting counter display...")

            # Initial display
            self.update_display(use_partial=False)

            start_time = time.time()

            while True:
                # Check if we should stop
                if duration_seconds and (time.time() - start_time) >= duration_seconds:
                    logger.info(
                        f"Display duration completed ({duration_seconds} seconds)"
                    )
                    break

                # Wait for 1 second
                time.sleep(1)

                # Increment counter
                self.counter += 1

                # Update display
                self.update_display(use_partial=True)

        except KeyboardInterrupt:
            logger.info("Counter display stopped by user")
        except Exception as e:
            logger.error(f"Error in counter display: {e}")
        finally:
            # Put display to sleep
            logger.info("Putting display to sleep...")
            self.epd.sleep()


def main():
    """Main function"""
    print("E-Paper Counter Display")
    print("Press Ctrl+C to stop")
    print()

    # Create and run the counter display
    counter_display = CounterDisplay()

    # Run for 60 seconds by default, or until interrupted
    counter_display.run(duration_seconds=60)


if __name__ == "__main__":
    main()
