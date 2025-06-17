#!/usr/bin/python3
"""
Simple test to isolate the Bad file descriptor error
"""

import sys
import os

# Add the lib directory to the path
script_dir = os.path.dirname(os.path.realpath(__file__))
libdir = os.path.join(script_dir, "lib")
sys.path.insert(0, libdir)


def test_simple_init():
    """Test simple initialization step by step"""
    print("Testing simple initialization...")

    try:
        from waveshare_epd.epd7in5b_V2 import EPD

        print("✅ EPD class imported successfully")

        epd = EPD()
        print("✅ EPD object created successfully")

        # Test module_init
        print("Testing module_init...")
        from waveshare_epd import epdconfig

        result = epdconfig.module_init()
        print(f"✅ module_init returned: {result}")

        # Test reset
        print("Testing reset...")
        epd.reset()
        print("✅ reset completed")

        # Test first command
        print("Testing first command...")
        epd.send_command(0x01)
        print("✅ first command sent")

        # Test first data
        print("Testing first data...")
        epd.send_data(0x07)
        print("✅ first data sent")

        # Test sleep
        print("Testing sleep...")
        epd.sleep()
        print("✅ sleep completed")

        return True

    except Exception as e:
        print(f"❌ Test failed at step: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_simple_init()
