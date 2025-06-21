#!/usr/bin/env python3

import sys
import os
from PIL import Image, ImageDraw, ImageFont
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
    debug_filename = f"test_processed_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.png"
    image.save(debug_filename)
    print(f"Saved test image: {debug_filename}")

    return image


def test_with_pixi_image():
    """Test with a sample Pixi-like image"""
    # Create a test image similar to what PixiJS might send
    width, height = 800, 480
    image = Image.new("RGB", (width, height), (255, 255, 255))  # White background
    draw = ImageDraw.Draw(image)

    # Draw some test content
    draw.rectangle([50, 50, 750, 430], fill=(0, 0, 0))  # Black border
    draw.rectangle([100, 100, 700, 380], fill=(255, 255, 255))  # White center

    # Draw some text
    try:
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24
        )
    except:
        font = ImageFont.load_default()

    draw.text((150, 150), "PixiJS Test Image", fill=(0, 0, 0), font=font)
    draw.text((150, 200), "This should be visible", fill=(0, 0, 0), font=font)
    draw.text((150, 250), "on the e-paper display", fill=(0, 0, 0), font=font)

    # Save original
    image.save("test_original.png")
    print("Saved original test image: test_original.png")

    # Process for e-paper
    epd_image = prepare_image_for_epd(image)

    # Test with e-paper display
    try:
        from waveshare_epd.epd7in5b_V2 import EPD

        print("Testing with real e-paper display...")

        epd = EPD()
        if epd.init() == 0:
            print("EPD initialized successfully")
            epd.Clear()

            buffer = epd.getbuffer(epd_image)
            red_buffer = [0x00] * (int(width / 8) * height)

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


if __name__ == "__main__":
    test_with_pixi_image()
