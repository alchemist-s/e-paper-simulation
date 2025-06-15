#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
Time Display Module for e-Paper Display
Provides functionality to display current time and date on e-paper displays
"""

import time
import datetime
from PIL import Image, ImageDraw, ImageFont
import os


class TimeDisplay:
    """Class for displaying time and date on e-paper displays"""

    def __init__(self, font_path=None, font_size=48):
        """
        Initialize TimeDisplay

        Args:
            font_path: Path to font file (optional)
            font_size: Font size for time display
        """
        self.font_path = font_path
        self.font_size = font_size
        self.font = None
        self._load_font()

    def _load_font(self):
        """Load the font for time display"""
        try:
            if self.font_path and os.path.exists(self.font_path):
                self.font = ImageFont.truetype(self.font_path, self.font_size)
            else:
                # Fallback to default font
                self.font = ImageFont.load_default()
        except Exception as e:
            print(f"Warning: Could not load font {self.font_path}: {e}")
            self.font = ImageFont.load_default()

    def get_current_time(self):
        """Get current time as formatted string"""
        now = datetime.datetime.now()
        return now.strftime("%H:%M:%S")

    def get_current_date(self):
        """Get current date as formatted string"""
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d")

    def get_current_weekday(self):
        """Get current weekday as formatted string"""
        now = datetime.datetime.now()
        return now.strftime("%A")

    def create_time_image(self, width, height, show_date=True, show_weekday=True):
        """
        Create an image with current time and date

        Args:
            width: Image width
            height: Image height
            show_date: Whether to show date
            show_weekday: Whether to show weekday

        Returns:
            PIL Image with time display
        """
        # Create a new image with white background
        image = Image.new("1", (width, height), 255)
        draw = ImageDraw.Draw(image)

        # Get current time and date
        time_str = self.get_current_time()
        date_str = self.get_current_date()
        weekday_str = self.get_current_weekday()

        # Calculate positions
        time_bbox = draw.textbbox((0, 0), time_str, font=self.font)
        time_width = time_bbox[2] - time_bbox[0]
        time_height = time_bbox[3] - time_bbox[1]

        # Center the time
        time_x = (width - time_width) // 2
        time_y = height // 2 - time_height - 20

        # Draw time
        draw.text((time_x, time_y), time_str, font=self.font, fill=0)

        # Draw date and weekday if requested
        if show_date or show_weekday:
            # Use smaller font for date/weekday
            small_font_size = self.font_size // 2
            try:
                if self.font_path and os.path.exists(self.font_path):
                    small_font = ImageFont.truetype(self.font_path, small_font_size)
                else:
                    small_font = ImageFont.load_default()
            except:
                small_font = ImageFont.load_default()

            y_offset = time_y + time_height + 30

            if show_weekday:
                weekday_bbox = draw.textbbox((0, 0), weekday_str, font=small_font)
                weekday_width = weekday_bbox[2] - weekday_bbox[0]
                weekday_x = (width - weekday_width) // 2
                draw.text((weekday_x, y_offset), weekday_str, font=small_font, fill=0)
                y_offset += small_font_size + 10

            if show_date:
                date_bbox = draw.textbbox((0, 0), date_str, font=small_font)
                date_width = date_bbox[2] - date_bbox[0]
                date_x = (width - date_width) // 2
                draw.text((date_x, y_offset), date_str, font=small_font, fill=0)

        return image

    def create_clock_image(self, width, height, show_seconds=True):
        """
        Create a clock-style image with current time

        Args:
            width: Image width
            height: Image height
            show_seconds: Whether to show seconds

        Returns:
            PIL Image with clock display
        """
        # Create a new image with white background
        image = Image.new("1", (width, height), 255)
        draw = ImageDraw.Draw(image)

        # Get current time
        now = datetime.datetime.now()
        hour = now.hour
        minute = now.minute
        second = now.second

        # Calculate clock center and radius
        center_x = width // 2
        center_y = height // 2
        radius = min(width, height) // 3

        # Draw clock circle
        draw.ellipse(
            (
                center_x - radius,
                center_y - radius,
                center_x + radius,
                center_y + radius,
            ),
            outline=0,
            width=3,
        )

        # Draw hour markers
        for i in range(12):
            angle = i * 30 - 90  # Start from 12 o'clock
            angle_rad = math.radians(angle)

            # Outer point
            outer_x = center_x + int((radius - 10) * math.cos(angle_rad))
            outer_y = center_y + int((radius - 10) * math.sin(angle_rad))

            # Inner point
            inner_x = center_x + int((radius - 30) * math.cos(angle_rad))
            inner_y = center_y + int((radius - 30) * math.sin(angle_rad))

            draw.line((outer_x, outer_y, inner_x, inner_y), fill=0, width=2)

        # Calculate hand angles
        hour_angle = (hour % 12 + minute / 60) * 30 - 90
        minute_angle = minute * 6 - 90
        second_angle = second * 6 - 90

        # Draw hour hand
        hour_length = radius * 0.5
        hour_x = center_x + int(hour_length * math.cos(math.radians(hour_angle)))
        hour_y = center_y + int(hour_length * math.sin(math.radians(hour_angle)))
        draw.line((center_x, center_y, hour_x, hour_y), fill=0, width=4)

        # Draw minute hand
        minute_length = radius * 0.7
        minute_x = center_x + int(minute_length * math.cos(math.radians(minute_angle)))
        minute_y = center_y + int(minute_length * math.sin(math.radians(minute_angle)))
        draw.line((center_x, center_y, minute_x, minute_y), fill=0, width=3)

        # Draw second hand if requested
        if show_seconds:
            second_length = radius * 0.8
            second_x = center_x + int(
                second_length * math.cos(math.radians(second_angle))
            )
            second_y = center_y + int(
                second_length * math.sin(math.radians(second_angle))
            )
            draw.line((center_x, center_y, second_x, second_y), fill=0, width=1)

        # Draw center dot
        draw.ellipse((center_x - 3, center_y - 3, center_x + 3, center_y + 3), fill=0)

        return image


# Add math import for clock functionality
import math
