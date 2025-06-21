#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import sys
import os
import time
import logging
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Add the lib directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))

from waveshare_epd import epd7in5b_V2

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SmartImageUpdater:
    def __init__(self):
        """Initialize the e-paper display for smart image updates"""
        self.epd = epd7in5b_V2.EPD()
        self.width = 800
        self.height = 480

        # Initialize the display for partial updates
        logger.info("Initializing e-paper display for partial updates...")
        if self.epd.init_part() != 0:
            logger.error("Failed to initialize e-paper display")
            sys.exit(1)

        # Clear the display initially
        self.epd.Clear()
        logger.info("Display initialized successfully")

        # Store the current display state
        self.current_image = None
        self.first_update = True

        # Configuration for change detection
        self.change_threshold = (
            10  # Minimum pixel difference to consider a region changed
        )
        self.min_region_size = 16  # Minimum region size to update (avoid tiny updates)
        self.max_regions = 10  # Maximum number of regions to update at once

    def prepare_image(self, image):
        """Prepare an image for display (resize, convert to 1-bit)"""
        if image.mode != "1":
            image = image.convert("1")

        # Resize if needed
        if image.size != (self.width, self.height):
            image = image.resize((self.width, self.height), Image.Resampling.LANCZOS)

        return image

    def detect_changes(self, new_image, old_image):
        """Detect changed regions between two images"""
        if old_image is None:
            # First update - return full image region
            return [(0, 0, self.width, self.height)]

        # Ensure both images are the same size and mode
        new_image = self.prepare_image(new_image)
        old_image = self.prepare_image(old_image)

        # Convert to numpy arrays for faster processing
        new_array = np.array(new_image)
        old_array = np.array(old_image)

        # Find differences
        diff_array = new_array != old_array

        if not np.any(diff_array):
            # No changes detected
            return []

        # Find connected regions of changes
        regions = self._find_connected_regions(diff_array)

        # Filter and merge regions
        filtered_regions = self._filter_regions(regions)

        return filtered_regions

    def _find_connected_regions(self, diff_array):
        """Find connected regions of changed pixels"""
        from scipy import ndimage

        # Label connected components
        labeled_array, num_features = ndimage.label(diff_array)

        regions = []
        for i in range(1, num_features + 1):
            # Find bounding box of this region
            coords = np.where(labeled_array == i)
            if len(coords[0]) > 0:
                y_min, y_max = coords[0].min(), coords[0].max()
                x_min, x_max = coords[1].min(), coords[1].max()

                # Add some padding around the region
                padding = 8
                x_min = max(0, x_min - padding)
                x_max = min(self.width - 1, x_max + padding)
                y_min = max(0, y_min - padding)
                y_max = min(self.height - 1, y_max + padding)

                regions.append((x_min, y_min, x_max, y_max))

        return regions

    def _filter_regions(self, regions):
        """Filter and merge regions"""
        if not regions:
            return []

        # Filter out regions that are too small
        filtered = []
        for x_min, y_min, x_max, y_max in regions:
            width = x_max - x_min
            height = y_max - y_min
            if width >= self.min_region_size and height >= self.min_region_size:
                filtered.append((x_min, y_min, x_max, y_max))

        # Sort by area (largest first)
        filtered.sort(key=lambda r: (r[2] - r[0]) * (r[3] - r[1]), reverse=True)

        # Limit number of regions
        if len(filtered) > self.max_regions:
            filtered = filtered[: self.max_regions]

        return filtered

    def _align_region_boundaries(self, x_min, y_min, x_max, y_max):
        """Align region boundaries to 8-byte boundaries for e-paper"""
        # Apply the same boundary adjustments as display_Partial
        if (
            (x_min % 8 + x_max % 8 == 8 and x_min % 8 > x_max % 8)
            or x_min % 8 + x_max % 8 == 0
            or (x_max - x_min) % 8 == 0
        ):
            x_min = x_min // 8 * 8
            x_max = x_max // 8 * 8
        else:
            x_min = x_min // 8 * 8
            if x_max % 8 == 0:
                x_max = x_max // 8 * 8
            else:
                x_max = x_max // 8 * 8 + 1

        return x_min, y_min, x_max, y_max

    def get_region_buffer(self, image, x_min, y_min, x_max, y_max):
        """Get buffer for a specific region"""
        # Align boundaries
        x_min, y_min, x_max, y_max = self._align_region_boundaries(
            x_min, y_min, x_max, y_max
        )

        # Crop the region from the full image
        region_image = image.crop((x_min, y_min, x_max, y_max))

        # Convert to buffer
        img = region_image.convert("1")
        buf = bytearray(img.tobytes("raw"))

        # Invert the bytes (same as getbuffer does)
        for i in range(len(buf)):
            buf[i] ^= 0xFF

        return buf, x_min, y_min, x_max, y_max

    def update_image(self, new_image):
        """Update the display with a new image, using partial updates for changed regions"""
        # Prepare the new image
        new_image = self.prepare_image(new_image)

        # Detect changed regions
        changed_regions = self.detect_changes(new_image, self.current_image)

        if not changed_regions and not self.first_update:
            logger.info("No changes detected - skipping update")
            return

        if self.first_update:
            # First update - use full display
            logger.info("First update - using full display")
            buffer = self.epd.getbuffer(new_image)
            red_buffer = [0x00] * (int(self.width / 8) * self.height)
            self.epd.display(buffer, red_buffer)
            self.first_update = False
        else:
            # Partial updates for changed regions
            logger.info(f"Updating {len(changed_regions)} changed regions")

            for i, (x_min, y_min, x_max, y_max) in enumerate(changed_regions):
                logger.info(
                    f"Updating region {i+1}/{len(changed_regions)}: ({x_min},{y_min}) to ({x_max},{y_max})"
                )

                # Get buffer for this region
                buffer, x_min_aligned, y_min_aligned, x_max_aligned, y_max_aligned = (
                    self.get_region_buffer(new_image, x_min, y_min, x_max, y_max)
                )

                # Update the region
                self.epd.display_Partial(
                    buffer, x_min_aligned, y_min_aligned, x_max_aligned, y_max_aligned
                )

        # Store the new image as current
        self.current_image = new_image.copy()

    def run_demo(self, duration=30):
        """Run a demo with changing images"""
        logger.info("Starting smart image update demo...")

        try:
            start_time = time.time()
            frame_count = 0

            while time.time() - start_time < duration:
                # Create a test image that changes over time
                image = self._create_test_image(frame_count)

                # Update the display
                self.update_image(image)

                frame_count += 1
                time.sleep(2)  # Update every 2 seconds

        except KeyboardInterrupt:
            logger.info("Demo stopped by user")
        finally:
            # Put display to sleep
            logger.info("Putting display to sleep...")
            self.epd.sleep()

    def _create_test_image(self, frame):
        """Create a test image that changes over time"""
        image = Image.new("1", (self.width, self.height), 255)
        draw = ImageDraw.Draw(image)

        # Draw a moving circle
        center_x = 200 + (frame * 20) % 400
        center_y = 240 + int(50 * np.sin(frame * 0.5))

        # Draw circle
        draw.ellipse(
            [center_x - 30, center_y - 30, center_x + 30, center_y + 30], fill=0
        )

        # Draw frame counter
        text = f"Frame: {frame}"
        try:
            font = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24
            )
        except:
            font = ImageFont.load_default()

        draw.text((50, 50), text, fill=0, font=font)

        # Draw some changing text
        messages = ["Hello", "World", "E-Paper", "Smart", "Updates"]
        message = messages[frame % len(messages)]
        draw.text((50, 100), message, fill=0, font=font)

        return image


def main():
    """Main function"""
    print("Smart Image Updater Demo")
    print("=======================")
    print("This demo shows how to detect changes between images")
    print("and apply only partial updates to changed regions.")
    print()

    # Create and run the smart image updater
    updater = SmartImageUpdater()

    # Run the demo
    updater.run_demo(duration=30)


if __name__ == "__main__":
    main()
