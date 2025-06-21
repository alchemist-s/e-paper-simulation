#!/usr/bin/env python3

import sys
import os
import numpy as np
from PIL import Image

# Add the lib directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))

# E-Paper display dimensions
EPD_WIDTH = 800
EPD_HEIGHT = 480


def prepare_image_for_epd(image):
    """Convert image to e-paper format (black and white, correct dimensions)"""
    print(f"Original image size: {image.size}, mode: {image.mode}")

    # Resize to e-paper dimensions
    image = image.resize((EPD_WIDTH, EPD_HEIGHT), Image.Resampling.LANCZOS)
    print(f"Resized image size: {image.size}")

    # Convert to 1-bit (black and white)
    if image.mode != "1":
        image = image.convert("1")

    print(f"Final image size: {image.size}, mode: {image.mode}")
    return image


def detect_changed_regions(new_image, old_image):
    """Detect regions that have changed between two images"""
    if old_image is None:
        # First image - return full display area
        return [(0, 0, EPD_WIDTH, EPD_HEIGHT)]

    # Ensure both images are the same size and format
    new_array = np.array(new_image)
    old_array = np.array(old_image)

    if new_array.shape != old_array.shape:
        # Size changed - return full area
        return [(0, 0, EPD_WIDTH, EPD_HEIGHT)]

    # Find differences
    diff_array = new_array != old_array

    if not np.any(diff_array):
        # No changes detected
        return []

    # Find connected regions of changes
    regions = find_connected_regions(diff_array)
    return regions


def find_connected_regions(diff_array):
    """Find connected regions of changed pixels"""
    from scipy import ndimage

    # Label connected components
    labeled_array, num_features = ndimage.label(diff_array)

    regions = []
    for i in range(1, num_features + 1):
        # Get coordinates of this region
        coords = np.where(labeled_array == i)
        if len(coords[0]) > 0:
            y_min, y_max = coords[0].min(), coords[0].max()
            x_min, x_max = coords[1].min(), coords[1].max()

            # Add some padding to ensure complete updates
            padding = 8
            x_min = max(0, x_min - padding)
            y_min = max(0, y_min - padding)
            x_max = min(EPD_WIDTH - 1, x_max + padding)
            y_max = min(EPD_HEIGHT - 1, y_max + padding)

            regions.append((x_min, y_min, x_max, y_max))

    return regions


def update_epd_partial(epd, image, regions):
    """Update specific regions of the e-paper display"""
    try:
        # Update each changed region
        for x_min, y_min, x_max, y_max in regions:
            # Align region boundaries to 8-byte boundaries for e-paper
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

            # Crop the region from the full image
            region_image = image.crop((x_min, y_min, x_max, y_max))

            # Use the EPD's getbuffer method
            buffer = epd.getbuffer(region_image)

            # Update the region
            epd.display_Partial(buffer, x_min, y_min, x_max, y_max)
            print(f"Updated region: ({x_min},{y_min}) to ({x_max},{y_max})")

        return True
    except Exception as e:
        print(f"Failed to update e-paper display: {e}")
        return False


def display_first_image(epd, epd_image):
    """Display the first image on e-paper"""
    print("Creating buffer for first display...")
    buffer = epd.getbuffer(epd_image)
    red_buffer = [0x00] * (int(EPD_WIDTH / 8) * EPD_HEIGHT)
    print(f"Buffer size: {len(buffer)}, Red buffer size: {len(red_buffer)}")
    print("Sending to e-paper display...")
    epd.display(buffer, red_buffer)
    print("First image displayed on e-paper")


def main():
    """Main function to handle image updates"""
    if len(sys.argv) < 2:
        print("Usage: python3 epd_updater.py <new_image_path> [previous_image_path]")
        sys.exit(1)

    new_image_path = sys.argv[1]
    previous_image_path = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"New image: {new_image_path}")
    print(f"Previous image: {previous_image_path}")

    # Load the new image
    try:
        new_image = Image.open(new_image_path)
        print(f"Successfully loaded new image: {new_image_path}")
    except Exception as e:
        print(f"Error loading new image: {e}")
        sys.exit(1)

    # Load the previous image if provided
    previous_image = None
    if previous_image_path and os.path.exists(previous_image_path):
        try:
            previous_image = Image.open(previous_image_path)
            print(f"Successfully loaded previous image: {previous_image_path}")
        except Exception as e:
            print(f"Error loading previous image: {e}")
            previous_image = None

    # Prepare images for e-paper
    new_epd_image = prepare_image_for_epd(new_image)
    previous_epd_image = (
        prepare_image_for_epd(previous_image) if previous_image else None
    )

    # Initialize e-paper display
    try:
        from waveshare_epd.epd7in5b_V2 import EPD

        print("Initializing e-paper display...")
        epd = EPD()

        # Re-initialize the display for each use (SPI connection needs to be fresh)
        if epd.init() == 0:
            print("EPD initialized successfully")
        else:
            print("Failed to initialize EPD")
            sys.exit(1)

        # Display images
        if previous_epd_image is None:
            # First image display
            print("First image - using full display update")
            display_first_image(epd, new_epd_image)
        else:
            # Detect changed regions and update partially
            print("Subsequent image - detecting changed regions")
            changed_regions = detect_changed_regions(new_epd_image, previous_epd_image)

            if changed_regions:
                print(f"Found {len(changed_regions)} changed regions, updating display")
                update_epd_partial(epd, new_epd_image, changed_regions)
                print(f"Updated {len(changed_regions)} regions on e-paper")
            else:
                print("No changes detected, skipping e-paper update")

        # Keep display awake for faster subsequent updates
        print("Update completed - display remains active")

    except Exception as e:
        print(f"Error with e-paper: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
