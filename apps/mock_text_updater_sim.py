#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
Mock Text Updater (Simulation)
A small demonstration of updating text every second using display_Partial
Runs in simulation mode without requiring hardware
"""

import sys
import os
import time
from PIL import Image, ImageDraw, ImageFont


class MockEPD:
    """Mock EPD class for simulation"""

    def __init__(self):
        self.width = 800
        self.height = 480
        self.partFlag = 1

        # Store the full display image
        self.display_image = Image.new("1", (self.width, self.height), 255)
        self.update_count = 0

    def init(self):
        """Initialize the mock display"""
        print("Mock EPD initialized")
        return 0

    def Clear(self):
        """Clear the display"""
        self.display_image = Image.new("1", (self.width, self.height), 255)
        print("Display cleared")

    def getbuffer(self, image):
        """Convert PIL image to buffer (simplified)"""
        # For simulation, we just return the image data
        return image

    def display_Partial(self, Image, Xstart, Ystart, Xend, Yend):
        """Simulate partial display update"""
        print(f"Partial update: region ({Xstart}, {Ystart}) to ({Xend}, {Yend})")

        # Convert buffer back to PIL image if needed
        if isinstance(Image, list):
            # This is a simplified conversion - in real implementation
            # you'd need proper buffer to image conversion
            print("Buffer received, would convert to image in real implementation")
        else:
            # Paste the partial image onto the full display
            self.display_image.paste(Image, (Xstart, Ystart))

        self.update_count += 1

        # Save the current state for visualization
        self.display_image.save(f"mock_display_state_{self.update_count:03d}.png")
        print(f"Display state saved as mock_display_state_{self.update_count:03d}.png")

    def sleep(self):
        """Put display to sleep"""
        print("Display put to sleep")


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
            try:
                # Try a different common font path
                self.font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 48)
            except:
                self.font = ImageFont.load_default()

    def create_text_image(self, text):
        """Create an image with the given text"""
        # Create image for the text region
        image = Image.new("1", (self.text_width, self.text_height), 255)
        draw = ImageDraw.Draw(image)

        # Get text bounding box
        bbox = draw.textbbox((0, 0), text, font=self.font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Center the text
        x = (self.text_width - text_width) // 2
        y = (self.text_height - text_height) // 2

        # Draw text
        draw.text((x, y), text, font=self.font, fill=0)

        return image

    def get_text_buffer(self, text):
        """Convert text image to buffer for display_Partial"""
        image = self.create_text_image(text)
        return self.epd.getbuffer(image)

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
        print("Starting text update demo (SIMULATION MODE)...")
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
        print(f"Total updates: {self.epd.update_count}")


def main():
    """Main function"""
    print("Mock Text Updater Demo (Simulation)")
    print("==================================")
    print()

    # Initialize the mock e-paper display
    try:
        epd = MockEPD()
        print("Initializing mock e-paper display...")
        epd.init()

        # Clear the display first
        print("Clearing display...")
        epd.Clear()

        # Create text updater
        updater = TextUpdater(epd)

        # Run the demo
        updater.run_demo(duration=10)

        # Put display to sleep
        print("Putting display to sleep...")
        epd.sleep()

        print("\nSimulation completed!")
        print("Check the generated PNG files to see the display states.")

    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
