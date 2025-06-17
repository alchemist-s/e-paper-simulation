#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
Data models for journey display system
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class TransportMode(Enum):
    """Transport mode enumeration"""

    TRAIN = "train"
    BUS = "bus"
    FERRY = "ferry"
    LIGHT_RAIL = "light_rail"


@dataclass
class JourneyStop:
    """Data model for a journey stop"""

    name: str
    departure_time: Optional[str]
    minutes_from_now: Optional[int]
    transport_mode: str
    line: str
    is_realtime: bool
    destination_name: Optional[str] = None
    platform: Optional[str] = None
    id: Optional[str] = None  # Add stop ID for destination matching
    arrival_time: Optional[str] = None  # Add arrival time for destination stops

    @property
    def time_display(self) -> str:
        """Format time for display"""
        if self.minutes_from_now is None:
            return "N/A"
        if self.minutes_from_now <= 0:
            return "Now"
        if self.minutes_from_now == 1:
            return "1 min"
        return f"{self.minutes_from_now} min"

    @property
    def clean_name(self) -> str:
        """Get cleaned station name"""
        if "Station, Platform" in self.name:
            return self.name.split("Station, Platform")[0].strip()
        return self.name

    @property
    def destination_primary(self) -> str:
        """Get primary destination name (before 'via')"""
        if not self.destination_name:
            return ""
        return self.destination_name.split(" via ")[0].strip()

    @property
    def destination_via(self) -> str:
        """Get 'via' part of destination"""
        if not self.destination_name or " via " not in self.destination_name:
            return ""
        return self.destination_name.split(" via ", 1)[1].strip()

    @property
    def platform_number(self) -> str:
        """Get platform number from name or platform property"""
        # First try to get from platform property (e.g., "RDS1" -> "1")
        if self.platform:
            # Extract number from platform code like "RDS1"
            import re

            numbers = re.findall(r"\d+", self.platform)
            if numbers:
                return numbers[0]

        # Fallback to extracting from station name
        if not self.name or "Platform" not in self.name:
            return ""
        try:
            # Extract platform number from "Station, Platform X, Station"
            platform_part = self.name.split("Platform")[1].split(",")[0].strip()
            return platform_part
        except (IndexError, AttributeError):
            return ""

    @property
    def line_number(self) -> str:
        """Extract just the line number (T1, T3, etc.) from the full line name"""
        if not self.line:
            return ""
        # Extract just the line number part (e.g., "T1" from "T1 North Shore Line")
        parts = self.line.split()
        if parts:
            return parts[0]  # Return first part (T1, T3, etc.)
        return self.line

    def is_valid(self) -> bool:
        """Check if stop data is valid"""
        is_valid = (
            self.departure_time is not None
            and self.minutes_from_now is not None
            and self.minutes_from_now >= 0
        )
        logger.debug(
            f"is_valid() for '{self.clean_name}': departure_time={self.departure_time}, minutes_from_now={self.minutes_from_now}, result={is_valid}"
        )
        return is_valid

    def is_destination_stop(self, destination_stop_id: str) -> bool:
        """Check if this stop is the destination stop"""
        return self.id == destination_stop_id


@dataclass
class DisplayConfig:
    """Configuration for display settings"""

    width: int = 800
    height: int = 480
    banner_height: int = 60
    info_box_height: int = 80  # Height for the new info box
    content_padding: int = 20
    stop_name_max_length: int = 35
    row_gap_padding: int = 10

    # Font configurations
    banner_font_size: int = 24
    line_font_size: int = 40  # Font size for line number in black box
    destination_font_size: int = 40  # Font size for destination name
    via_font_size: int = 14  # Font size for "via" text
    platform_font_size: int = 40  # Font size for platform number
    stop_font_size: int = 40
    time_font_size: int = 48
    no_data_font_size: int = 24

    # Font paths
    font_paths: dict = field(
        default_factory=lambda: {
            "arial": "/System/Library/Fonts/Arial.ttf",
            "arial_bold": "/System/Library/Fonts/Arial Bold.ttf",
        }
    )


@dataclass
class JourneyConfig:
    """Configuration for journey settings"""

    origin_stop_id: str = "213891"  # Rhodes
    destination_stop_id: str = "10101100"  # Central
    update_interval: int = 60  # seconds
    max_stops_display: int = 10
