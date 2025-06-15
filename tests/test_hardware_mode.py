#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
Test script to verify hardware mode works correctly
"""

import sys
import os

# Add the lib directory to the path (go up one level from tests/)
script_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
libdir = os.path.join(script_dir, "lib")
sys.path.insert(0, libdir)

from display_factory import DisplayFactory
from time_display import TimeDisplay


def test_hardware_mode_creation():
    """Test that hardware mode can be created when e-paper module is available"""

    print("Testing hardware mode creation...")

    try:
        # Try to import the e-paper module
        from waveshare_epd import epd7in5b_V2

        print("✅ E-paper module imported successfully")

        # Try to create hardware display
        display = DisplayFactory.create_display(simulate=False, epd_module=epd7in5b_V2)
        print("✅ Hardware display created successfully")

        # Test time display creation
        time_display = TimeDisplay(font_size=64)
        time_image = time_display.create_time_image(
            800, 480, show_date=True, show_weekday=True
        )
        print("✅ Time display image created successfully")

        return True

    except ImportError as e:
        print(f"❌ E-paper module not available: {e}")
        print("This is expected if you're not on a Raspberry Pi with e-paper hardware.")
        return False
    except Exception as e:
        print(f"❌ Hardware mode test failed: {e}")
        return False


def test_simulation_mode():
    """Test that simulation mode still works"""

    print("Testing simulation mode...")

    try:
        # Create simulation display
        display = DisplayFactory.create_display(simulate=True, width=800, height=480)
        print("✅ Simulation display created successfully")

        # Test time display
        time_display = TimeDisplay(font_size=64)
        time_image = time_display.create_time_image(
            800, 480, show_date=True, show_weekday=True
        )
        print("✅ Time display works in simulation mode")

        return True

    except Exception as e:
        print(f"❌ Simulation mode test failed: {e}")
        return False


def main():
    """Main test function"""

    print("Hardware Mode Test")
    print("==================")
    print()

    # Test hardware mode
    hardware_ok = test_hardware_mode_creation()
    print()

    # Test simulation mode
    simulation_ok = test_simulation_mode()
    print()

    if hardware_ok:
        print("🎉 Hardware mode is ready! You can run:")
        print("  python3 examples/live_clock.py")
        print("  python3 examples/time_example.py")
        print("  python3 main.py --clock")
    elif simulation_ok:
        print("✅ Simulation mode works! Use --simulate flag:")
        print("  python3 examples/live_clock.py --simulate")
        print("  python3 examples/time_example.py --simulate")
        print("  python3 main.py --simulate --clock")
    else:
        print("❌ Both modes failed. Please check the installation.")


if __name__ == "__main__":
    main()
