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

        # Initialize the display
        logger.info("Initializing e-paper display...")
        if self.epd.init() != 0:
            logger.error("Failed to initialize e-paper display")
            sys.exit(1)

        # Clear the display initially
        self.epd.Clear()
        logger.info("Display initialized successfully")

    def create_text_image(self, text, font_size=None):
        """Create an image with the given text"""
        if font_size is None:
            font_size = self.font_size

        # Create a new image with white background
        image = Image.new("1", (self.epd.width, self.epd.height), self.bg_color)
        draw = ImageDraw.Draw(image)

        # Try to use a system font, fallback to default if not available
        try:
            # Try different font options
            font_options = [
                "/System/Library/Fonts/Arial.ttf",  # macOS
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
                "/usr/share/fonts/TTF/Arial.ttf",  # Some Linux distros
            ]

            font = None
            for font_path in font_options:
                if os.path.exists(font_path):
                    font = ImageFont.truetype(font_path, font_size)
                    break

            if font is None:
                # Use default font
                font = ImageFont.load_default()
                logger.warning("Using default font - text may not display optimally")
        except Exception as e:
            logger.warning(f"Could not load system font: {e}")
            font = ImageFont.load_default()

        # Calculate text position to center it
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (self.epd.width - text_width) // 2
        y = (self.epd.height - text_height) // 2

        # Draw the text
        draw.text((x, y), text, fill=self.text_color, font=font)

        # Store text position for partial updates
        self.text_x = x
        self.text_y = y
        self.text_width = text_width
        self.text_height = text_height

        return image

    def update_display(self, use_partial=True):
        """Update the display with the current counter value"""
        text = f"Counter {self.counter}"
        logger.info(f"Updating display: {text}")

        if use_partial and self.counter > 0:
            # For partial updates, create a smaller image with just the text
            padding = 10
            x_start = max(0, self.text_x - padding)
            x_end = min(self.epd.width, self.text_x + self.text_width + padding)
            y_start = max(0, self.text_y - padding)
            y_end = min(self.epd.height, self.text_y + self.text_height + padding)

            # Create a smaller image for the partial update region
            region_width = x_end - x_start
            region_height = y_end - y_start

            # Create image for just this region
            region_image = Image.new("1", (region_width, region_height), self.bg_color)
            region_draw = ImageDraw.Draw(region_image)

            # Try to use a system font, fallback to default if not available
            try:
                font_options = [
                    "/System/Library/Fonts/Arial.ttf",  # macOS
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
                    "/usr/share/fonts/TTF/Arial.ttf",  # Some Linux distros
                ]

                font = None
                for font_path in font_options:
                    if os.path.exists(font_path):
                        font = ImageFont.truetype(font_path, self.font_size)
                        break

                if font is None:
                    font = ImageFont.load_default()
            except Exception as e:
                font = ImageFont.load_default()

            # Calculate text position relative to the region
            text_x_in_region = self.text_x - x_start
            text_y_in_region = self.text_y - y_start

            # Draw the text in the region
            region_draw.text(
                (text_x_in_region, text_y_in_region),
                text,
                fill=self.text_color,
                font=font,
            )

            # Get the buffer for just this region
            buffer = self.epd.getbuffer(region_image)

            # Update only the specific region
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
