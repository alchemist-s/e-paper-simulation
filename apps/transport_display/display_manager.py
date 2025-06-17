#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
Display management for journey display system
"""

from PIL import Image
import logging

from .models import DisplayConfig

logger = logging.getLogger(__name__)


class LiveDisplayManager:
    """Manages live display updates using tkinter"""

    def __init__(self, config: DisplayConfig):
        self.config = config
        self.root = None
        self.image_label = None
        self._setup_window()

    def _setup_window(self) -> None:
        """Setup tkinter window"""
        try:
            import tkinter as tk
            from PIL import ImageTk

            self.root = tk.Tk()
            self.root.title("Journey Display - Live View")
            self.root.geometry(f"{self.config.width}x{self.config.height}")

            self.image_label = tk.Label(self.root)
            self.image_label.pack(expand=True, fill="both")

        except ImportError:
            logger.warning("tkinter not available, live display disabled")
            self.root = None

    def update_display(self, image: Image.Image) -> None:
        """Update the live display"""
        if not self.root:
            return

        try:
            from PIL import ImageTk

            photo = ImageTk.PhotoImage(image)
            self.image_label.config(image=photo)
            self.image_label.image = photo  # Keep reference
            self.root.update()

        except Exception as e:
            logger.error(f"Error updating live display: {e}")

    def close(self) -> None:
        """Close the live display window"""
        if self.root:
            self.root.quit()
            self.root.destroy()


class MockEPD:
    """Mock EPD class for simulation"""

    def __init__(self, config: DisplayConfig, show_live: bool = False):
        self.config = config
        self.show_live = show_live
        self.display_image = Image.new("1", (config.width, config.height), 255)
        self.update_count = 0
        self.live_display = LiveDisplayManager(config) if show_live else None

    def init(self) -> int:
        """Initialize the mock display"""
        logger.info("Mock EPD initialized")
        return 0

    def clear(self) -> None:
        """Clear the display"""
        self.display_image = Image.new(
            "1", (self.config.width, self.config.height), 255
        )
        logger.info("Display cleared")

    def update_display(self, image: Image.Image) -> None:
        """Update the display with new image"""
        self.display_image = image
        self.update_count += 1

        # Save display state
        filename = f"journey_display_{self.update_count:03d}.png"
        self.display_image.save(filename)
        logger.info(f"Journey display saved as {filename}")

        # Update live display if enabled
        if self.live_display:
            self.live_display.update_display(image)

    def sleep(self) -> None:
        """Put display to sleep"""
        logger.info("Display put to sleep")
        if self.live_display:
            self.live_display.close()
