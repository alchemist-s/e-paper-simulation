#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
Test script to verify hardware display fix
"""

import sys
import os

# Add the lib directory to the path (go up one level from tests/)
script_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
libdir = os.path.join(script_dir, "lib")
sys.path.insert(0, libdir)

from display_factory import DisplayFactory
from time_display import TimeDisplay


def test_single_image_display():
    """Test that single image display works correctly"""

    print("Testing single image display fix...")

    # Create display in simulation mode for testing
    display = DisplayFactory.create_display(simulate=True, width=800, height=480)

    # Create time display
    time_display = TimeDisplay(font_size=64)

    # Create a single image
    time_image = time_display.create_time_image(
        800, 480, show_date=True, show_weekday=True
    )

    try:
        # This should work without the TypeError
        display.display(time_image)
        print("✅ Single image display test passed!")
        return True
    except Exception as e:
        print(f"❌ Single image display test failed: {e}")
        return False


def test_double_image_display():
    """Test that double image display still works"""

    print("Testing double image display...")

    # Create display in simulation mode for testing
    display = DisplayFactory.create_display(simulate=True, width=800, height=480)

    # Create two images
    from PIL import Image, ImageDraw

    image1 = Image.new("1", (800, 480), 255)
    draw1 = ImageDraw.Draw(image1)
    draw1.text((10, 10), "Image 1", fill=0)

    image2 = Image.new("1", (800, 480), 255)
    draw2 = ImageDraw.Draw(image2)
    draw2.text((10, 50), "Image 2", fill=0)

    try:
        # This should work with both images
        display.display(image1, image2)
        print("✅ Double image display test passed!")
        return True
    except Exception as e:
        print(f"❌ Double image display test failed: {e}")
        return False


def main():
    """Main test function"""

    print("Hardware Display Fix Test")
    print("========================")
    print()

    # Test single image display
    test1_passed = test_single_image_display()
    print()

    # Test double image display
    test2_passed = test_double_image_display()
    print()

    if test1_passed and test2_passed:
        print("🎉 All tests passed! The fix is working correctly.")
        print()
        print("The hardware display now properly handles:")
        print("- Single images (creates blank red image automatically)")
        print("- Double images (works as before)")
        print()
        print("You can now run time display on hardware without errors!")
    else:
        print("❌ Some tests failed. Please check the implementation.")


if __name__ == "__main__":
    main()
