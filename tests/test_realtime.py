#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
Quick Real-time Test
Demonstrates time updates in simulation mode
"""

import sys
import os
import time
from datetime import datetime

# Add the lib directory to the path (go up one level from tests/)
script_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
libdir = os.path.join(script_dir, "lib")
sys.path.insert(0, libdir)

from display_factory import DisplayFactory
from time_display import TimeDisplay


def main():
    """Quick test of real-time updates"""

    # Create display
    display = DisplayFactory.create_display(simulate=True, width=800, height=480)
    display.init()
    display.clear()

    # Create time display
    time_display = TimeDisplay(font_size=64)

    print("Real-time Time Display Test")
    print("===========================")
    print("You should see the time updating in the window!")
    print("Press Ctrl+C to exit")
    print()

    try:
        # Show 5 updates at 2-second intervals
        for i in range(5):
            current_time = datetime.now()
            print(f"Update {i+1}/5: {current_time.strftime('%H:%M:%S')}")

            # Create and display time image
            time_image = time_display.create_time_image(
                display.width, display.height, show_date=True, show_weekday=True
            )
            display.display(time_image)

            time.sleep(2)

        print("Test complete! Window will stay open.")

    except KeyboardInterrupt:
        print("\nTest interrupted")

    # Keep window open
    display.run()


if __name__ == "__main__":
    main()
