#!/usr/bin/env python3

import sys
import os

# Add the lib directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))


def main():
    """Put the e-paper display to sleep"""
    try:
        from waveshare_epd.epd7in5b_V2 import EPD

        print("Connecting to e-paper display...")
        epd = EPD()

        # Put display to sleep
        print("Putting display to sleep...")
        epd.sleep()
        print("Display put to sleep successfully")

    except Exception as e:
        print(f"Error putting EPD to sleep: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
