#!/usr/bin/python3
"""
Test to check what the init method returns
"""

import sys
import os

# Add the lib directory to the path
script_dir = os.path.dirname(os.path.realpath(__file__))
libdir = os.path.join(script_dir, "lib")
sys.path.insert(0, libdir)


def test_init_return():
    """Test what init method returns"""
    print("Testing init method return value...")

    try:
        from waveshare_epd.epd7in5b_V2 import EPD

        print("✅ EPD class imported successfully")

        epd = EPD()
        print("✅ EPD object created successfully")

        # Test init and check return value
        result = epd.init()
        print(f"✅ EPD init returned: {result} (type: {type(result)})")

        # Test sleep
        epd.sleep()
        print("✅ EPD sleep completed")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_init_return()
