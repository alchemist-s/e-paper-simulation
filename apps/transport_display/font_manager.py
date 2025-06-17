#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
Font management for journey display system
"""

from typing import Dict, Optional
from PIL import ImageFont
import logging

logger = logging.getLogger(__name__)


class FontManager:
    """Manages font loading and caching"""

    def __init__(self, config):
        self.config = config
        self._fonts: Dict[str, ImageFont.FreeTypeFont] = {}
        self._default_font = ImageFont.load_default()

    def get_font(
        self, font_type: str, size: Optional[int] = None
    ) -> ImageFont.FreeTypeFont:
        """Get font with caching"""
        cache_key = f"{font_type}_{size}"

        if cache_key in self._fonts:
            return self._fonts[cache_key]

        try:
            if font_type == "arial":
                font_path = self.config.font_paths["arial"]
            elif font_type == "arial_bold":
                font_path = self.config.font_paths["arial_bold"]
            else:
                return self._default_font

            font_size = size or getattr(self.config, f"{font_type}_font_size", 12)
            font = ImageFont.truetype(font_path, font_size)
            self._fonts[cache_key] = font
            return font

        except (OSError, IOError):
            logger.warning(f"Could not load font {font_type}, using default")
            return self._default_font
