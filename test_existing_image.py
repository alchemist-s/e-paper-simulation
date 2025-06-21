#!/usr/bin/env python3

import sys
import os
from PIL import Image
from datetime import datetime

# Add the lib directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))


def prepare_image_for_epd(image):
    """Convert image to e-paper format (black and white, correct dimensions)"""
    EPD_WIDTH = 800
    EPD_HEIGHT = 480

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
        f"test_existing_processed_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.png"
    )
    image.save(debug_filename)
    print(f"Saved processed image: {debug_filename}")

    return image


def test_existing_pixi_image():
    """Test with an existing PixiJS image"""
    pixi_images_dir = "pixi_images"

    # List available images
    images = [f for f in os.listdir(pixi_images_dir) if f.endswith(".png")]
    print(f"Available PixiJS images: {images}")

    if not images:
        print("No images found in pixi_images directory")
        return

    # Use the most recent image
    latest_image = sorted(images)[-1]
    image_path = os.path.join(pixi_images_dir, latest_image)
    print(f"Testing with image: {latest_image}")

    # Load the image
    try:
        original_image = Image.open(image_path)
        print(f"Successfully loaded image: {image_path}")

        # Save a copy of the original for comparison
        original_copy = f"test_original_{latest_image}"
        original_image.save(original_copy)
        print(f"Saved original copy: {original_copy}")

        # Process for e-paper
        epd_image = prepare_image_for_epd(original_image)

        # Test with e-paper display
        try:
            from waveshare_epd.epd7in5b_V2 import EPD

            print("Testing with real e-paper display...")

            epd = EPD()
            if epd.init() == 0:
                print("EPD initialized successfully")
                epd.Clear()

                buffer = epd.getbuffer(epd_image)
                red_buffer = [0x00] * (int(800 / 8) * 480)

                print(f"Buffer size: {len(buffer)}")
                print("Displaying processed image...")
                epd.display(buffer, red_buffer)
                print("Image displayed!")

                epd.sleep()
                print("Display put to sleep")
            else:
                print("Failed to initialize EPD")

        except Exception as e:
            print(f"Error with e-paper: {e}")
            import traceback

            traceback.print_exc()

    except Exception as e:
        print(f"Error loading image: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_existing_pixi_image()
