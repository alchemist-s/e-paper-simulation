#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
Text Display Module
A module for displaying text on e-paper displays
"""

import os
from PIL import Image, ImageDraw, ImageFont
from module_interface import DisplayModule


class TextModule(DisplayModule):
    """Module for displaying text"""

    def __init__(self, **config):
        """
        Initialize the text module

        Args:
            **config: Configuration parameters
                - text: Text to display
                - font_path: Path to font file
                - font_size: Font size
                - color: Text color (0 for black, 255 for white)
                - align: Text alignment ('left', 'center', 'right')
                - valign: Vertical alignment ('top', 'center', 'bottom')
        """
        super().__init__(**config)

        # Default configuration
        self.text = config.get("text", "Hello World")
        self.font_path = config.get("font_path")
        self.font_size = config.get("font_size", 24)
        self.color = config.get("color", 0)  # Black text
        self.align = config.get("align", "center")
        self.valign = config.get("valign", "center")

        # Load font
        self.font = self._load_font()

    def _load_font(self):
        """Load the font for text display"""
        try:
            if self.font_path and os.path.exists(self.font_path):
                return ImageFont.truetype(self.font_path, self.font_size)
            else:
                return ImageFont.load_default()
        except Exception as e:
            print(f"Warning: Could not load font {self.font_path}: {e}")
            return ImageFont.load_default()

    def set_text(self, text: str):
        """Update the text to display"""
        self.text = text

    def render(self, width: int, height: int) -> Image.Image:
        """
        Render the text module

        Args:
            width: Available width for rendering
            height: Available height for rendering

        Returns:
            PIL Image containing the rendered text
        """
        # Create a new image with white background
        image = Image.new("1", (width, height), 255)
        draw = ImageDraw.Draw(image)

        # Get text bounding box
        bbox = draw.textbbox((0, 0), self.text, font=self.font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Calculate position based on alignment
        if self.align == "left":
            x = 10
        elif self.align == "right":
            x = width - text_width - 10
        else:  # center
            x = (width - text_width) // 2

        if self.valign == "top":
            y = 10
        elif self.valign == "bottom":
            y = height - text_height - 10
        else:  # center
            y = (height - text_height) // 2

        # Draw text
        draw.text((x, y), self.text, font=self.font, fill=self.color)

        return image
