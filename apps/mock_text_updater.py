#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
Mock Text Updater
A small demonstration of updating text every second using display_Partial
"""

import sys
import os
import time
from PIL import Image, ImageDraw, ImageFont

# Add the lib directory to the path
script_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
libdir = os.path.join(script_dir, "lib")
sys.path.insert(0, libdir)

from waveshare_epd.epd7in5b_V2 import EPD


class TextUpdater:
    """Simple text updater that tracks regions for partial updates"""

    def __init__(self, epd):
        self.epd = epd
        self.width = 800
        self.height = 480

        # Text region tracking
        self.text_x = 50
        self.text_y = 200
        self.text_width = 700
        self.text_height = 80

        # Font setup
        try:
            self.font = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48
            )
        except:
            self.font = ImageFont.load_default()

    def create_text_image(self, text):
        """Create an image with the given text"""
        # Create full-size image for the display
        image = Image.new("1", (self.width, self.height), 255)
        draw = ImageDraw.Draw(image)

        # Get text bounding box
        bbox = draw.textbbox((0, 0), text, font=self.font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Center the text within the text region
        x = self.text_x + (self.text_width - text_width) // 2
        y = self.text_y + (self.text_height - text_height) // 2

        # Draw text
        draw.text((x, y), text, font=self.font, fill=0)

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

        # Create buffer of the correct size
        buffer_size = width_bytes * height
        buf = [0x00] * buffer_size

        # Create a simple pattern that changes with the counter
        # This will help us see if partial updates are working
        pattern = 0xFF if int(text.split()[-1]) % 2 == 0 else 0x00
        for i in range(buffer_size):
            buf[i] = pattern

        return buf

    def update_text(self, text):
        """Update the text using display_Partial"""
        print(f"Updating text to: {text}")

        # Get buffer for the text region
        buffer = self.get_text_buffer(text)

        # Calculate region coordinates
        x_start = self.text_x
        y_start = self.text_y
        x_end = self.text_x + self.text_width
        y_end = self.text_y + self.text_height

        # Update the specific region
        self.epd.display_Partial(buffer, x_start, y_start, x_end, y_end)

    def run_demo(self, duration=10):
        """Run the demo for specified duration in seconds"""
        print("Starting text update demo...")
        print(f"Will update every second for {duration} seconds")
        print("Press Ctrl+C to stop early")
        print()

        start_time = time.time()
        counter = 0

        try:
            while time.time() - start_time < duration:
                # Create text with counter
                text = f"Counter: {counter:03d}"

                # Update the display
                self.update_text(text)

                counter += 1
                time.sleep(1)

        except KeyboardInterrupt:
            print("\nDemo stopped by user")

        print("Demo completed!")


def main():
    """Main function"""
    print("Mock Text Updater Demo")
    print("=====================")
    print()

    # Initialize the e-paper display
    try:
        epd = EPD()
        print("Initializing e-paper display for partial updates...")
        epd.init_part()  # Use init_part() for partial updates

        # Clear the display first
        print("Clearing display...")
        epd.Clear()

        # Create text updater
        updater = TextUpdater(epd)

        # Run the demo
        updater.run_demo(duration=50)

        # Put display to sleep
        print("Putting display to sleep...")
        epd.sleep()

    except Exception as e:
        print(f"Error: {e}")
        print(
            "Make sure you have the proper hardware connected or run in simulation mode"
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
