#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
Display renderer for journey display system
"""

from typing import List
from datetime import datetime
from PIL import Image, ImageDraw
import logging

from .models import JourneyStop, DisplayConfig
from .font_manager import FontManager

logger = logging.getLogger(__name__)


class DisplayRenderer:
    """Handles rendering of journey display"""

    def __init__(self, config: DisplayConfig):
        self.config = config
        self.font_manager = FontManager(config)

    def render_banner(self, draw: ImageDraw.Draw) -> None:
        """Render the top banner"""
        # Black background
        draw.rectangle([0, 0, self.config.width, self.config.banner_height], fill=0)

        banner_font = self.font_manager.get_font("arial", self.config.banner_font_size)

        # Left side: "Next Service"
        left_text = "Next Service"
        left_bbox = draw.textbbox((0, 0), left_text, font=banner_font)
        left_x = self.config.content_padding
        left_y = (self.config.banner_height - (left_bbox[3] - left_bbox[1])) // 2
        draw.text((left_x, left_y), left_text, font=banner_font, fill=255)

        # Right side: Current time
        current_time = datetime.now().strftime("%H:%M")
        time_label = f"Time now: {current_time}"
        right_bbox = draw.textbbox((0, 0), time_label, font=banner_font)
        right_width = right_bbox[2] - right_bbox[0]
        right_x = self.config.width - right_width - self.config.content_padding
        right_y = (self.config.banner_height - (right_bbox[3] - right_bbox[1])) // 2
        draw.text((right_x, right_y), time_label, font=banner_font, fill=255)

    def render_info_box(self, draw: ImageDraw.Draw, next_stop: JourneyStop) -> None:
        """Render the info box below banner with line, destination, and platform"""
        logger.debug(
            f"Rendering info box for: Line={next_stop.line}, Destination={next_stop.destination_name}, Platform={next_stop.platform_number}"
        )

        info_box_y = self.config.banner_height
        info_box_end_y = info_box_y + self.config.info_box_height

        # Background for info box (light gray)
        draw.rectangle([0, info_box_y, self.config.width, info_box_end_y], fill=240)

        # Left column: Line number and destination
        left_column_x = self.config.content_padding

        # Line number in black box with rounded corners
        line_text = next_stop.line_number
        line_font = self.font_manager.get_font("arial_bold", self.config.line_font_size)
        line_bbox = draw.textbbox((0, 0), line_text, font=line_font)
        line_width = line_bbox[2] - line_bbox[0]
        line_height = line_bbox[3] - line_bbox[1]

        # Bigger black box for line number with rounded corners
        line_box_padding = 24  # Increased padding
        line_box_width = line_width + (line_box_padding * 2)
        line_box_height = line_height + (line_box_padding * 2)
        line_box_x = left_column_x
        line_box_y = info_box_y + 15  # Slightly lower position

        # Draw rounded rectangle using PIL's rounded_rectangle method
        corner_radius = 8
        draw.rounded_rectangle(
            [
                line_box_x,
                line_box_y,
                line_box_x + line_box_width,
                line_box_y + line_box_height,
            ],
            radius=corner_radius,
            fill=0,
        )

        # Center text in black box
        line_text_x = line_box_x + line_box_width // 2 - line_width // 2
        # Adjust vertical centering to account for text baseline
        line_text_y = (
            line_box_y + line_box_height // 2 - line_height // 2 - 8
        )  # Slight upward adjustment
        draw.text((line_text_x, line_text_y), line_text, font=line_font, fill=255)

        # Destination info to the right of line box
        dest_x = line_box_x + line_box_width + 20  # Increased spacing

        # Primary destination (e.g., "North Sydney") - bigger font
        if next_stop.destination_primary:
            dest_font = self.font_manager.get_font(
                "arial_bold", self.config.destination_font_size + 4  # Bigger font
            )
            dest_bbox = draw.textbbox(
                (0, 0), next_stop.destination_primary, font=dest_font
            )
            dest_height = dest_bbox[3] - dest_bbox[1]

            draw.text(
                (dest_x, line_box_y),
                next_stop.destination_primary,
                font=dest_font,
                fill=0,
            )

            # "via Central" in smaller text below
            if next_stop.destination_via:
                via_text = f"via {next_stop.destination_via}"
                via_font = self.font_manager.get_font(
                    "arial", self.config.via_font_size
                )
                via_y = line_box_y + dest_height + 8  # Use actual destination height
                draw.text((dest_x, via_y), via_text, font=via_font, fill=0)

        # Right column: Platform number
        platform_text = next_stop.platform_number
        if platform_text:
            platform_font = self.font_manager.get_font(
                "arial_bold", self.config.platform_font_size
            )
            platform_bbox = draw.textbbox((0, 0), platform_text, font=platform_font)
            platform_width = platform_bbox[2] - platform_bbox[0]
            platform_height = platform_bbox[3] - platform_bbox[1]

            # Center platform text in right column
            platform_x = (
                self.config.width - platform_width - self.config.content_padding
            )
            platform_y = (
                info_box_y + (self.config.info_box_height - platform_height) // 2
            )

            draw.text(
                (platform_x, platform_y), platform_text, font=platform_font, fill=0
            )

    def render_stops_list(self, draw: ImageDraw.Draw, stops: List[JourneyStop]) -> None:
        """Render the list of stops"""
        if not stops:
            self._render_no_data(draw)
            return

        stop_font = self.font_manager.get_font("arial", self.config.stop_font_size)

        # Calculate row spacing
        try:
            font_bbox = stop_font.getbbox("Ag")
            font_height = font_bbox[3] - font_bbox[1]
            row_gap = font_height + self.config.row_gap_padding
        except:
            row_gap = 45

        # Render stops - adjust starting position for info box
        content_start_y = (
            self.config.banner_height
            + self.config.info_box_height
            + self.config.content_padding
        )
        current_y = content_start_y

        for i, stop in enumerate(stops):
            if current_y + 50 > self.config.height:
                logger.info(f"Truncating stops list at stop {i} due to height limit")
                break

            stop_name = stop.clean_name
            if len(stop_name) > self.config.stop_name_max_length:
                stop_name = stop_name[: self.config.stop_name_max_length - 3] + "..."

            draw.text(
                (self.config.content_padding, current_y),
                stop_name,
                font=stop_font,
                fill=0,
            )
            current_y += row_gap

        # Render next service time in bottom right
        self._render_next_service_time(draw, stops[0])

    def _render_next_service_time(
        self, draw: ImageDraw.Draw, next_stop: JourneyStop
    ) -> None:
        """Render the next service time in bottom right corner"""
        time_font = self.font_manager.get_font("arial_bold", self.config.time_font_size)
        time_text = next_stop.time_display

        time_bbox = draw.textbbox((0, 0), time_text, font=time_font)
        time_width = time_bbox[2] - time_bbox[0]
        time_height = time_bbox[3] - time_bbox[1]
        time_x = self.config.width - time_width - 40
        time_y = self.config.height - time_height - 40

        draw.text((time_x, time_y), time_text, font=time_font, fill=0)

    def _render_no_data(self, draw: ImageDraw.Draw) -> None:
        """Render no data message"""
        no_data_font = self.font_manager.get_font(
            "arial", self.config.no_data_font_size
        )
        no_data_text = "No journey data available"

        bbox = draw.textbbox((0, 0), no_data_text, font=no_data_font)
        text_width = bbox[2] - bbox[0]
        text_x = (self.config.width - text_width) // 2
        text_y = (self.config.height - (bbox[3] - bbox[1])) // 2

        draw.text((text_x, text_y), no_data_text, font=no_data_font, fill=0)

    def create_journey_display(self, stops: List[JourneyStop]) -> Image.Image:
        """Create the complete journey display image"""
        image = Image.new("1", (self.config.width, self.config.height), 255)
        draw = ImageDraw.Draw(image)

        self.render_banner(draw)

        if stops:
            self.render_info_box(draw, stops[0])
            self.render_stops_list(draw, stops)
        else:
            self._render_no_data(draw)

        return image
