#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
Time Display Example
Demonstrates how to use the TimeDisplay class with e-paper displays
"""

import sys
import os
import time

# Add the lib directory to the path
script_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
libdir = os.path.join(script_dir, "lib")
sys.path.insert(0, libdir)

from display_factory import DisplayFactory
from time_display import TimeDisplay


def main():
    """Main function to demonstrate time display"""

    # Create display (simulation mode for testing)
    display = DisplayFactory.create_display(simulate=True, width=800, height=480)

    # Initialize display
    display.init()
    display.clear()

    # Create TimeDisplay instance
    time_display = TimeDisplay(font_size=64)

    print("Time Display Example")
    print("===================")

    # Show digital time
    print("1. Showing digital time...")
    time_image = time_display.create_time_image(
        display.width, display.height, show_date=True, show_weekday=True
    )
    display.display(time_image)
    time.sleep(3)

    # Show analog clock
    print("2. Showing analog clock...")
    clock_image = time_display.create_clock_image(
        display.width, display.height, show_seconds=True
    )
    display.display(clock_image)
    time.sleep(3)

    # Show time only (no date/weekday)
    print("3. Showing time only...")
    time_only_image = time_display.create_time_image(
        display.width, display.height, show_date=False, show_weekday=False
    )
    display.display(time_only_image)
    time.sleep(3)

    # Clear display
    display.clear()

    print("Example complete!")

    # Keep window open in simulation mode
    display.run()


if __name__ == "__main__":
    main()
