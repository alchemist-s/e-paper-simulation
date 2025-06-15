#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
import argparse
import logging
import time
from PIL import Image, ImageDraw, ImageFont

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.realpath(__file__))

# Set up paths
picdir = os.path.join(script_dir, "pic")
libdir = os.path.join(script_dir, "lib")

# Add lib directory to Python path
if os.path.exists(libdir):
    sys.path.insert(0, libdir)
    logging.info(f"Added lib directory to path: {libdir}")
else:
    logging.error(f"Lib directory not found: {libdir}")
    sys.exit(1)

try:
    from display_factory import DisplayFactory

    logging.info("Successfully imported DisplayFactory")
except ImportError as e:
    logging.error(f"Failed to import DisplayFactory: {e}")
    logging.error(f"Current sys.path: {sys.path}")
    sys.exit(1)

logging.basicConfig(level=logging.DEBUG)

try:
    parser = argparse.ArgumentParser(description="e-Paper demo with simulation option")
    parser.add_argument(
        "--simulate",
        action="store_true",
        help="Simulate display using Tkinter real-time window",
    )
    args = parser.parse_args()
    simulate = args.simulate

    logging.info("epd7in5b_V2 Demo")

    # Create display implementation
    if simulate:
        display = DisplayFactory.create_display(simulate=True, width=800, height=480)
    else:
        from waveshare_epd import epd7in5b_V2

        display = DisplayFactory.create_display(simulate=False, epd_module=epd7in5b_V2)

    # Initialize display
    logging.info("init and Clear")
    display.init()
    display.clear()

    font24 = ImageFont.truetype(os.path.join(picdir, "Font.ttc"), 24)
    font18 = ImageFont.truetype(os.path.join(picdir, "Font.ttc"), 18)

    # Drawing on the Horizontal image
    logging.info("1.Drawing on the Horizontal image...")
    Himage = Image.new(
        "1", (display.width, display.height), 255
    )  # 255: clear the frame
    Other = Image.new("1", (display.width, display.height), 255)  # 255: clear the frame
    draw_Himage = ImageDraw.Draw(Himage)
    draw_other = ImageDraw.Draw(Other)
    draw_Himage.text((10, 0), "hello world", font=font24, fill=0)
    draw_Himage.text((10, 20), "7.5inch e-Paper B", font=font24, fill=0)
    draw_Himage.text((150, 0), "微雪电子", font=font24, fill=0)
    draw_other.line((20, 50, 70, 100), fill=0)
    draw_other.line((70, 50, 20, 100), fill=0)
    draw_other.rectangle((20, 50, 70, 100), outline=0)
    draw_other.line((165, 50, 165, 100), fill=0)
    draw_Himage.line((140, 75, 190, 75), fill=0)
    draw_Himage.arc((140, 50, 190, 100), 0, 360, fill=0)
    draw_Himage.rectangle((80, 50, 130, 100), fill=0)
    draw_Himage.chord((200, 50, 250, 100), 0, 360, fill=0)

    display.display(Himage, Other)
    if not simulate:
        time.sleep(2)

    # Drawing on the Vertical image
    logging.info("2.Drawing on the Vertical image...")
    Limage = Image.new(
        "1", (display.height, display.width), 255
    )  # 255: clear the frame
    Limage_Other = Image.new(
        "1", (display.height, display.width), 255
    )  # 255: clear the frame
    draw_Himage = ImageDraw.Draw(Limage)
    draw_Himage_Other = ImageDraw.Draw(Limage_Other)
    draw_Himage.text((2, 0), "hello world", font=font18, fill=0)
    draw_Himage.text((2, 20), "7.5inch epd", font=font18, fill=0)
    draw_Himage_Other.text((20, 50), "微雪电子", font=font18, fill=0)
    draw_Himage_Other.line((10, 90, 60, 140), fill=0)
    draw_Himage_Other.line((60, 90, 10, 140), fill=0)
    draw_Himage_Other.rectangle((10, 90, 60, 140), outline=0)
    draw_Himage_Other.line((95, 90, 95, 140), fill=0)
    draw_Himage.line((70, 115, 120, 115), fill=0)
    draw_Himage.arc((70, 90, 120, 140), 0, 360, fill=0)
    draw_Himage.rectangle((10, 150, 60, 200), fill=0)
    draw_Himage.chord((70, 150, 120, 200), 0, 360, fill=0)

    display.display(Limage, Limage_Other)
    if not simulate:
        time.sleep(2)

    logging.info("3.read bmp file")
    display.init_fast()
    Himage = Image.open(os.path.join(picdir, "7in5_V2_b.bmp"))
    Himage_Other = Image.open(os.path.join(picdir, "7in5_V2_r.bmp"))
    display.display(Himage, Himage_Other)
    if not simulate:
        time.sleep(2)

    logging.info("Clear...")
    display.init()
    display.clear()

    logging.info("Goto Sleep...")
    if simulate:
        # For simulation, start the Tkinter main loop to keep window open
        display.run()
    else:
        display.sleep()

except IOError as e:
    logging.info(e)

except KeyboardInterrupt:
    logging.info("ctrl + c:")
    if not simulate:
        epd7in5b_V2.epdconfig.module_exit(cleanup=True)
    exit()
