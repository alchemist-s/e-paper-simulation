#!/usr/bin/env python3

import sys
import os

# Add the lib directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))


def main():
    """Initialize the e-paper display"""
    try:
        from waveshare_epd.epd7in5b_V2 import EPD

        print("Initializing e-paper display...")
        epd = EPD()

        # Initialize for partial updates
        if epd.init_part() != 0:
            print("Failed to initialize e-paper display for partial updates")
            sys.exit(1)

        # Clear the display
        print("Clearing display...")
        epd.Clear()
        print("Display cleared successfully")

        # Put display to sleep
        epd.sleep()
        print("Display put to sleep")
        print("EPD initialization completed successfully")

    except Exception as e:
        print(f"Error initializing EPD: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
