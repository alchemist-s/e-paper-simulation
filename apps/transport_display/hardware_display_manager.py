#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
Hardware display management for journey display system
"""

import sys
import os
from PIL import Image
import logging

# Add the lib directory to the path
script_dir = os.path.dirname(os.path.realpath(__file__))
libdir = os.path.join(script_dir, "..", "..", "lib")
sys.path.insert(0, libdir)

from display_factory import DisplayFactory
from .models import DisplayConfig

logger = logging.getLogger(__name__)


class HardwareDisplayManager:
    """Manages hardware e-paper display integration"""

    def __init__(self, config: DisplayConfig, simulate: bool = False, epd_module=None):
        self.config = config
        self.simulate = simulate
        self.epd_module = epd_module
        self.display = None
        self.epd_raw = None  # Raw e-paper object for partial updates
        self.update_count = 0
        self._setup_display()

    def _setup_display(self) -> None:
        """Setup the display using the factory"""
        try:
            if self.simulate:
                self.display = DisplayFactory.create_display(
                    simulate=True, width=self.config.width, height=self.config.height
                )
                logger.info("Using simulation display")
            else:
                if self.epd_module is None:
                    # Default to epd7in5b_V2 since that's what's available
                    try:
                        from waveshare_epd.epd7in5b_V2 import EPD

                        self.epd_module = EPD
                        logger.info("Using default e-paper module: epd7in5b_V2")
                    except ImportError:
                        raise ValueError(
                            "Default e-paper module epd7in5b_V2 not available. "
                            "Please provide epd_module or use --simulate flag."
                        )

                self.display = DisplayFactory.create_display(
                    simulate=False, epd_module=self.epd_module
                )

                # Get the raw e-paper object for partial updates
                if hasattr(self.display, "epd"):
                    self.epd_raw = self.display.epd

                logger.info("Using hardware display")

        except Exception as e:
            logger.error(f"Failed to setup display: {e}")
            raise

    def init(self) -> int:
        """Initialize the display"""
        try:
            if self.simulate:
                # Simulation mode should always succeed
                self.display.init()
                logger.info("Simulation display initialized successfully")
                return 0
            else:
                # Hardware mode
                result = self.display.init()

                # For hardware mode, also initialize partial mode
                if result == 0 and self.epd_raw:
                    try:
                        self.epd_raw.init_part()
                        logger.info("Partial mode initialized")
                    except Exception as e:
                        logger.warning(f"Failed to initialize partial mode: {e}")
                        # Don't fail the entire initialization if partial mode fails
                        # Partial mode is optional for basic functionality

                logger.info("Hardware display initialized successfully")
                return result

        except Exception as e:
            logger.error(f"Failed to initialize display: {e}")
            return 1

    def clear(self) -> None:
        """Clear the display"""
        try:
            self.display.clear()
            logger.info("Display cleared")
        except Exception as e:
            logger.error(f"Failed to clear display: {e}")

    def update_display(self, image: Image.Image) -> None:
        """Update the display with new image (full update)"""
        try:
            self.display_image = image
            self.update_count += 1

            # Save display state for debugging
            filename = f"journey_display_{self.update_count:03d}.png"
            self.display_image.save(filename)
            logger.info(f"Journey display saved as {filename}")

            # Display on hardware/simulation
            self.display.display(self.display_image)
            logger.info(f"Display updated (update #{self.update_count})")

        except Exception as e:
            logger.error(f"Failed to update display: {e}")

    def update_partial(self, image: Image.Image, region: tuple) -> None:
        """Update a specific region of the display using partial update"""
        try:
            if self.simulate:
                # For simulation, just log the partial update without saving full image
                self.update_count += 1
                logger.info(
                    f"Simulation partial update (region: {region}, update #{self.update_count})"
                )
                # Still call display.display() to show in Tkinter if available
                self.display.display(image)
                return

            if not self.epd_raw:
                logger.warning("No raw e-paper object available for partial update")
                return

            # Convert image to buffer format
            img_1bit = image.convert("1")
            buf = bytearray(img_1bit.tobytes("raw"))

            # Invert bytes (same as getbuffer in epd7in5b_V2)
            for i in range(len(buf)):
                buf[i] ^= 0xFF

            # Perform partial update
            x_start, y_start, x_end, y_end = region
            self.epd_raw.display_Partial(buf, x_start, y_start, x_end, y_end)

            self.update_count += 1
            logger.info(
                f"Partial update completed (region: {region}, update #{self.update_count})"
            )

        except Exception as e:
            logger.error(f"Failed to perform partial update: {e}")

    def sleep(self) -> None:
        """Put display to sleep"""
        try:
            self.display.sleep()
            logger.info("Display put to sleep")
        except Exception as e:
            logger.error(f"Failed to put display to sleep: {e}")

    @property
    def width(self) -> int:
        """Get display width"""
        return self.display.width if self.display else self.config.width

    @property
    def height(self) -> int:
        """Get display height"""
        return self.display.height if self.display else self.config.height
