#!/usr/bin/env python3

import sys
import os
import numpy as np
from PIL import Image
from datetime import datetime

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

    # Save debug image
    debug_filename = (
        f"debug_epd_processed_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.png"
    )
    image.save(debug_filename)
    print(f"Saved processed image: {debug_filename}")

    return image


def detect_changes(new_image, old_image):
    """Detect changed regions between two images"""
    if old_image is None:
        # First update - return full image region
        return [(0, 0, EPD_WIDTH, EPD_HEIGHT)]

    # Ensure both images are the same size and mode
    new_image = prepare_image_for_epd(new_image)
    old_image = prepare_image_for_epd(old_image)

    # Convert to numpy arrays for faster processing
    new_array = np.array(new_image)
    old_array = np.array(old_image)

    # Find differences
    diff_array = new_array != old_array

    if not np.any(diff_array):
        # No changes detected
        return []

    # Fast clustering approach - find changed pixels and group them
    changed_pixels = np.where(diff_array)
    if len(changed_pixels[0]) == 0:
        return []

    # Convert to list of (y, x) coordinates
    coords = list(zip(changed_pixels[0], changed_pixels[1]))

    # Simple distance-based clustering
    regions = fast_cluster_regions(coords)

    # Filter and limit regions
    filtered_regions = filter_regions(regions)

    print(f"Found {len(filtered_regions)} regions from {len(coords)} changed pixels")
    return filtered_regions


def fast_cluster_regions(coords, max_distance=50):
    """Fast clustering of coordinates into regions using grid-based approach"""
    if not coords:
        return []

    # Convert to grid-based clustering for speed
    grid_size = max_distance
    grid = {}

    # Group pixels by grid cells
    for y, x in coords:
        grid_y = y // grid_size
        grid_x = x // grid_size
        grid_key = (grid_y, grid_x)

        if grid_key not in grid:
            grid[grid_key] = []
        grid[grid_key].append((y, x))

    # Merge adjacent grid cells
    regions = []
    processed = set()

    for grid_key, pixels in grid.items():
        if grid_key in processed:
            continue

        # Start a new region
        region_pixels = pixels.copy()
        processed.add(grid_key)

        # Find adjacent grid cells
        grid_y, grid_x = grid_key
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dy == 0 and dx == 0:
                    continue

                neighbor_key = (grid_y + dy, grid_x + dx)
                if neighbor_key in grid and neighbor_key not in processed:
                    region_pixels.extend(grid[neighbor_key])
                    processed.add(neighbor_key)

        # Calculate bounding box for this region
        if region_pixels:
            ys = [p[0] for p in region_pixels]
            xs = [p[1] for p in region_pixels]
            y_min, y_max = min(ys), max(ys)
            x_min, x_max = min(xs), max(xs)

            # Add padding
            padding = 16
            x_min = max(0, x_min - padding)
            x_max = min(EPD_WIDTH - 1, x_max + padding)
            y_min = max(0, y_min - padding)
            y_max = min(EPD_HEIGHT - 1, y_max + padding)

            regions.append((x_min, y_min, x_max, y_max))

    return regions


def filter_regions(regions):
    """Filter regions by size and limit count"""
    if not regions:
        return []

    # Filter by minimum size
    min_size = 32
    filtered = []
    for x_min, y_min, x_max, y_max in regions:
        width = x_max - x_min
        height = y_max - y_min
        if width >= min_size and height >= min_size:
            filtered.append((x_min, y_min, x_max, y_max))

    # Sort by area (largest first)
    filtered.sort(key=lambda r: (r[2] - r[0]) * (r[3] - r[1]), reverse=True)

    # Limit to top 5 regions
    max_regions = 5
    if len(filtered) > max_regions:
        filtered = filtered[:max_regions]

    return filtered


def update_epd_partial(epd, image, regions):
    """Update specific regions of the e-paper display"""
    try:
        # Update each changed region
        for i, (x_min, y_min, x_max, y_max) in enumerate(regions):
            print(
                f"Updating region {i+1}/{len(regions)}: ({x_min},{y_min}) to ({x_max},{y_max})"
            )

            # Ensure all values are integers
            x_min = int(x_min)
            y_min = int(y_min)
            x_max = int(x_max)
            y_max = int(y_max)

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

            print(f"Aligned region: ({x_min},{y_min}) to ({x_max},{y_max})")

            # Crop the region from the full image
            region_image = image.crop((x_min, y_min, x_max, y_max))

            # Convert to 1-bit and get buffer (for partial updates, don't invert bytes)
            region_image_1bit = region_image.convert("1")
            buffer = bytearray(region_image_1bit.tobytes("raw"))

            # Note: display_Partial() doesn't invert bytes back like display() does
            # so we don't invert them here

            # Update the region using display_Partial
            epd.display_Partial(buffer, x_min, y_min, x_max, y_max)
            print(f"Updated region: ({x_min},{y_min}) to ({x_max},{y_max})")

        return True
    except Exception as e:
        print(f"Failed to update e-paper display: {e}")
        import traceback

        traceback.print_exc()
        return False


def merge_regions(regions, merge_distance=32):
    """Merge regions that are close together or overlapping"""
    if not regions:
        return []

    if len(regions) == 1:
        return regions

    # Sort regions by x coordinate
    sorted_regions = sorted(regions, key=lambda r: r[0])

    merged = []
    current = list(sorted_regions[0])

    for x_min, y_min, x_max, y_max in sorted_regions[1:]:
        # Check if this region overlaps or is close to current region
        if (
            x_min <= current[2] + merge_distance
            and x_max >= current[0] - merge_distance
            and y_min <= current[3] + merge_distance
            and y_max >= current[1] - merge_distance
        ):

            # Merge regions
            current[0] = min(current[0], x_min)  # x_min
            current[1] = min(current[1], y_min)  # y_min
            current[2] = max(current[2], x_max)  # x_max
            current[3] = max(current[3], y_max)  # y_max
        else:
            # No overlap, add current region and start new one
            merged.append(tuple(current))
            current = [x_min, y_min, x_max, y_max]

    # Add the last region
    merged.append(tuple(current))

    print(f"Merged {len(regions)} regions into {len(merged)} regions")
    return merged


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

    # Save current and previous images for debugging
    if previous_epd_image:
        previous_epd_image.save(
            f"debug_previous_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.png"
        )
    new_epd_image.save(
        f"debug_current_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.png"
    )
    print("Saved debug images for comparison")

    # Initialize e-paper display
    try:
        from waveshare_epd.epd7in5b_V2 import EPD

        print("Initializing e-paper display...")
        epd = EPD()

        # For first image, use fast initialization to establish white background
        if previous_epd_image is None:
            print("First image - using fast initialization for clean white background")
            if epd.init_Fast() == 0:
                print("EPD initialized successfully with fast mode")
            else:
                print("Failed to initialize EPD")
                sys.exit(1)
        else:
            # For subsequent images, use partial update initialization
            print("Subsequent image - using partial update initialization")
            if epd.init_part() == 0:
                print("EPD initialized successfully for partial updates")
            else:
                print("Failed to initialize EPD")
                sys.exit(1)

        # Display images
        if previous_epd_image is None:
            # First image display - use full display method with blank red buffer (like counter example)
            print("First image - using full display method with blank red buffer")
            buffer = epd.getbuffer(new_epd_image)
            # Create a blank red buffer (no red content) - same as counter example
            red_buffer = [0x00] * (int(EPD_WIDTH / 8) * EPD_HEIGHT)
            epd.display(buffer, red_buffer)
            print("First image displayed successfully")
        else:
            # Detect changed regions and update partially
            print("Subsequent image - detecting changed regions")
            changed_regions = detect_changes(new_epd_image, previous_epd_image)

            if changed_regions:
                print(f"Found {len(changed_regions)} changed regions, updating display")

                # Merge overlapping or nearby regions
                merged_regions = merge_regions(changed_regions)
                print(
                    f"Merged {len(changed_regions)} regions into {len(merged_regions)} regions"
                )

                # Update the regions using partial display
                update_epd_partial(epd, new_epd_image, merged_regions)
                print(f"Updated {len(merged_regions)} regions on e-paper")
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
