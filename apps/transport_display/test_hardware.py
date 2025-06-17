#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
Test script for hardware integration
"""

import sys
import os
import logging

# Add the lib directory to the path
script_dir = os.path.dirname(os.path.realpath(__file__))
libdir = os.path.join(script_dir, "..", "..", "lib")
sys.path.insert(0, libdir)

from .hardware_display_manager import HardwareDisplayManager
from .models import DisplayConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_simulation_mode():
    """Test simulation mode"""
    print("Testing simulation mode...")

    config = DisplayConfig()
    display = HardwareDisplayManager(config, simulate=True)

    # Test initialization
    result = display.init()
    print(f"Init result: {result}")

    # Test display update
    from PIL import Image

    test_image = Image.new("1", (config.width, config.height), 255)
    display.update_display(test_image)

    # Test sleep
    display.sleep()
    print("Simulation mode test completed successfully!")


def test_hardware_mode():
    """Test hardware mode (if available)"""
    print("Testing hardware mode...")

    try:
        config = DisplayConfig()
        display = HardwareDisplayManager(config, simulate=False)

        # Test initialization
        result = display.init()
        print(f"Init result: {result}")

        if result == 0:
            # Test display update
            from PIL import Image

            test_image = Image.new("1", (config.width, config.height), 255)
            display.update_display(test_image)

            # Test sleep
            display.sleep()
            print("Hardware mode test completed successfully!")
        else:
            print("Hardware initialization failed")

    except Exception as e:
        print(f"Hardware mode test failed: {e}")
        print(
            "This is normal if no hardware is connected or waveshare-epaper is not installed"
        )


def main():
    """Main test function"""
    print("Transport Display Hardware Test")
    print("===============================")
    print()

    # Test simulation mode
    test_simulation_mode()
    print()

    # Test hardware mode
    test_hardware_mode()
    print()

    print("All tests completed!")


if __name__ == "__main__":
    main()
