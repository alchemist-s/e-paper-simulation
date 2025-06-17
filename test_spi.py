#!/usr/bin/python3
"""
Simple SPI test to diagnose hardware issues
"""

import sys
import os

# Add the lib directory to the path
script_dir = os.path.dirname(os.path.realpath(__file__))
libdir = os.path.join(script_dir, "lib")
sys.path.insert(0, libdir)


def test_spi_basic():
    """Test basic SPI functionality"""
    print("Testing basic SPI functionality...")

    try:
        import spidev

        print("✅ spidev imported successfully")

        spi = spidev.SpiDev()
        print("✅ SpiDev created successfully")

        # Try to open SPI device
        spi.open(0, 0)
        print("✅ SPI device opened successfully")

        spi.max_speed_hz = 4000000
        spi.mode = 0b00
        print("✅ SPI configured successfully")

        spi.close()
        print("✅ SPI device closed successfully")

        return True

    except Exception as e:
        print(f"❌ SPI test failed: {e}")
        return False


def test_gpio_basic():
    """Test basic GPIO functionality"""
    print("\nTesting basic GPIO functionality...")

    try:
        import gpiozero

        print("✅ gpiozero imported successfully")

        # Test LED creation (this should work even without hardware)
        led = gpiozero.LED(17)
        print("✅ LED object created successfully")

        led.close()
        print("✅ LED object closed successfully")

        return True

    except Exception as e:
        print(f"❌ GPIO test failed: {e}")
        return False


def test_epd_config():
    """Test e-paper configuration"""
    print("\nTesting e-paper configuration...")

    try:
        from waveshare_epd import epdconfig

        print("✅ epdconfig imported successfully")

        # Check which implementation is being used
        print(f"Implementation type: {type(epdconfig.implementation).__name__}")

        # Test module_init
        result = epdconfig.module_init()
        print(f"✅ module_init returned: {result}")

        # Test module_exit
        epdconfig.module_exit()
        print("✅ module_exit completed")

        return True

    except Exception as e:
        print(f"❌ EPD config test failed: {e}")
        return False


def test_epd_init():
    """Test e-paper initialization"""
    print("\nTesting e-paper initialization...")

    try:
        from waveshare_epd.epd7in5b_V2 import EPD

        print("✅ EPD class imported successfully")

        epd = EPD()
        print("✅ EPD object created successfully")

        # Test initialization
        result = epd.init()
        print(f"✅ EPD init returned: {result}")

        # Test sleep
        epd.sleep()
        print("✅ EPD sleep completed")

        return True

    except Exception as e:
        print(f"❌ EPD init test failed: {e}")
        return False


def main():
    """Main test function"""
    print("SPI and E-Paper Hardware Test")
    print("=============================")
    print()

    # Test basic SPI
    spi_ok = test_spi_basic()

    # Test basic GPIO
    gpio_ok = test_gpio_basic()

    # Test e-paper config
    epd_config_ok = test_epd_config()

    # Test e-paper init
    epd_init_ok = test_epd_init()

    print("\n" + "=" * 50)
    print("TEST RESULTS:")
    print(f"SPI Basic: {'✅ PASS' if spi_ok else '❌ FAIL'}")
    print(f"GPIO Basic: {'✅ PASS' if gpio_ok else '❌ FAIL'}")
    print(f"EPD Config: {'✅ PASS' if epd_config_ok else '❌ FAIL'}")
    print(f"EPD Init: {'✅ PASS' if epd_init_ok else '❌ FAIL'}")

    if all([spi_ok, gpio_ok, epd_config_ok, epd_init_ok]):
        print("\n🎉 All tests passed! Hardware should work correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")


if __name__ == "__main__":
    main()
