#!/usr/bin/python3
"""
Test to check if init_part() is causing the initialization issue
"""

import sys
import os

# Add the lib directory to the path
script_dir = os.path.dirname(os.path.realpath(__file__))
libdir = os.path.join(script_dir, "lib")
sys.path.insert(0, libdir)


def test_init_part():
    """Test init_part() method"""
    print("Testing init_part() method...")

    try:
        from waveshare_epd.epd7in5b_V2 import EPD

        print("✅ EPD class imported successfully")

        epd = EPD()
        print("✅ EPD object created successfully")

        # Test regular init
        result = epd.init()
        print(f"✅ EPD init returned: {result}")

        # Test init_part
        try:
            result_part = epd.init_part()
            print(f"✅ EPD init_part returned: {result_part}")
        except Exception as e:
            print(f"❌ EPD init_part failed: {e}")
            return False

        # Test sleep
        epd.sleep()
        print("✅ EPD sleep completed")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    test_init_part()
