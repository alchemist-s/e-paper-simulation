#!/usr/bin/env python3

import sys
import os
from PIL import Image, ImageDraw, ImageFont

# Add the lib directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))

try:
    from waveshare_epd.epd7in5b_V2 import EPD

    print("EPD library imported successfully")

    # Create a simple test image
    width, height = 800, 480
    image = Image.new("1", (width, height), 255)  # White background
    draw = ImageDraw.Draw(image)

    # Draw a black rectangle
    draw.rectangle([100, 100, 700, 380], fill=0)

    # Draw white text
    try:
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36
        )
    except:
        font = ImageFont.load_default()

    draw.text((200, 200), "E-Paper Test", fill=255, font=font)
    draw.text((200, 250), "If you see this,", fill=255, font=font)
    draw.text((200, 300), "the display works!", fill=255, font=font)

    # Initialize and display
    print("Initializing EPD...")
    epd = EPD()

    if epd.init() == 0:
        print("EPD initialized successfully")
        epd.Clear()

        # Get buffer and display
        buffer = epd.getbuffer(image)
        red_buffer = [0x00] * (int(width / 8) * height)

        print("Displaying image...")
        epd.display(buffer, red_buffer)
        print("Image displayed!")

        # Sleep the display
        epd.sleep()
        print("Display put to sleep")
    else:
        print("Failed to initialize EPD")

except Exception as e:
    print(f"Error: {e}")
    import traceback

    traceback.print_exc()
