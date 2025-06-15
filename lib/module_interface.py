#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
Module Interface for E-Paper Display
Defines the base interface for display modules that can be composed together
"""

from abc import ABC, abstractmethod
from PIL import Image
from typing import Dict, Any, Optional


class DisplayModule(ABC):
    """Abstract base class for display modules"""

    def __init__(self, **config):
        """
        Initialize the module with configuration

        Args:
            **config: Module-specific configuration parameters
        """
        self.config = config
        self._width = config.get("width", 800)
        self._height = config.get("height", 480)
        self.refresh_interval = config.get(
            "refresh_interval", None
        )  # in seconds, None = static
        self.last_updated = 0  # epoch timestamp

    @abstractmethod
    def render(self, width: int, height: int) -> Image.Image:
        """
        Render the module content to an image

        Args:
            width: Available width for rendering
            height: Available height for rendering

        Returns:
            PIL Image containing the rendered content
        """
        pass

    @property
    def width(self) -> int:
        """Module width"""
        return self._width

    @property
    def height(self) -> int:
        """Module height"""
        return self._height

    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)

    def set_config(self, key: str, value: Any) -> None:
        """Set configuration value"""
        self.config[key] = value

    def should_update(self, now: Optional[float] = None) -> bool:
        """
        Determine if the module should be updated based on refresh_interval.
        Args:
            now: Current time (epoch seconds). If None, uses time.time().
        Returns:
            True if the module should be updated, False otherwise.
        """
        import time

        if self.refresh_interval is None:
            return False  # static module
        if now is None:
            now = time.time()
        return (now - self.last_updated) >= self.refresh_interval

    def mark_updated(self, now: Optional[float] = None):
        """
        Mark the module as updated (set last_updated to now).
        Args:
            now: Current time (epoch seconds). If None, uses time.time().
        """
        import time

        if now is None:
            now = time.time()
        self.last_updated = now


class ModuleContainer:
    """Container for composing multiple modules into a view"""

    def __init__(self, width: int, height: int):
        """
        Initialize the module container

        Args:
            width: Total display width
            height: Total display height
        """
        self.width = width
        self.height = height
        self.modules = []
        self.layout = "vertical"  # 'vertical', 'horizontal', 'grid'
        self._module_images = []  # cache of rendered module images

    def add_module(self, module: DisplayModule, position: Optional[Dict] = None):
        """
        Add a module to the container

        Args:
            module: DisplayModule instance
            position: Optional position dict with x, y, width, height
        """
        if position is None:
            position = {}

        module_info = {"module": module, "position": position}
        self.modules.append(module_info)
        self._module_images.append(None)  # keep cache in sync

    def render(self, now: Optional[float] = None) -> Image.Image:
        """
        Render all modules into a single image, only updating modules as needed.
        Args:
            now: Current time (epoch seconds). If None, uses time.time().
        Returns:
            PIL Image containing all modules
        """
        import time

        if now is None:
            now = time.time()
        image = Image.new("1", (self.width, self.height), 255)

        for idx, module_info in enumerate(self.modules):
            module = module_info["module"]
            position = module_info["position"]
            x = position.get("x", 0)
            y = position.get("y", 0)
            width = position.get("width", module.width)
            height = position.get("height", module.height)

            # Only re-render if needed
            if self._module_images[idx] is None or module.should_update(now):
                module_image = module.render(width, height)
                self._module_images[idx] = module_image
                module.mark_updated(now)
            else:
                module_image = self._module_images[idx]

            image.paste(module_image, (x, y))

        return image

    def clear(self):
        """Remove all modules"""
        self.modules.clear()
        self._module_images.clear()

    def get_module(self, index: int) -> Optional[DisplayModule]:
        """Get module by index"""
        if 0 <= index < len(self.modules):
            return self.modules[index]["module"]
        return None

    def remove_module(self, index: int) -> bool:
        """Remove module by index"""
        if 0 <= index < len(self.modules):
            del self.modules[index]
            del self._module_images[index]
            return True
        return False
