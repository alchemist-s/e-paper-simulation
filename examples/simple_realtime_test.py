#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
Simple Real-time Test
Tests real-time updates with proper Tkinter handling
"""

import sys
import os
import time
from datetime import datetime

# Add the lib directory to the path
script_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
libdir = os.path.join(script_dir, "lib")
sys.path.insert(0, libdir)

from display_factory import DisplayFactory
from time_display import TimeDisplay


def main():
    """Main function to test real-time updates"""

    # Create display (simulation mode for testing)
    display = DisplayFactory.create_display(simulate=True, width=800, height=480)

    # Initialize display
    display.init()
    display.clear()

    # Create TimeDisplay instance
    time_display = TimeDisplay(font_size=64)

    print("Simple Real-time Test")
    print("====================")
    print("This test will show the time updating every 3 seconds")
    print("Press Ctrl+C to exit")
    print()

    try:
        # Show 10 updates at 3-second intervals
        for i in range(10):
            current_time = datetime.now()
            time_str = current_time.strftime("%H:%M:%S")
            date_str = current_time.strftime("%Y-%m-%d")
            weekday_str = current_time.strftime("%A")

            print(f"Update {i+1}/10: {time_str} - {weekday_str}, {date_str}")

            # Create time image
            time_image = time_display.create_time_image(
                display.width, display.height, show_date=True, show_weekday=True
            )

            # Display the time
            display.display(time_image)

            # Wait 3 seconds before next update
            time.sleep(3)

        print("\nTest complete!")

    except KeyboardInterrupt:
        print("\nTest interrupted by user")

    # Keep window open in simulation mode
    display.run()


if __name__ == "__main__":
    main()
