#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
Journey data service for fetching and processing transport data
"""

import sys
import os
from typing import List
import logging

# Add the lib directory to the path
script_dir = os.path.dirname(os.path.realpath(__file__))
libdir = os.path.join(script_dir, "..", "..", "lib")
sys.path.insert(0, libdir)

from transport_api import TransportNSWAPI
from .models import JourneyStop, JourneyConfig

logger = logging.getLogger(__name__)


class JourneyDataService:
    """Service for fetching and processing journey data"""

    def __init__(self, api_key: str, config: JourneyConfig):
        self.api = TransportNSWAPI(api_key)
        self.config = config

    def get_journey_stops(self) -> List[JourneyStop]:
        """Fetch and process journey stops"""
        try:
            logger.info("Fetching journey stops from API...")

            raw_stops = self.api.get_simplified_journey_stops(
                self.config.origin_stop_id, self.config.destination_stop_id
            )

            if not raw_stops:
                logger.warning("No journey stops returned from API")
                return []

            # Convert to JourneyStop objects
            journey_stops = []
            for i, stop in enumerate(raw_stops):
                logger.debug(f"Processing stop {i}: {stop}")
                logger.debug(f"Stop {i} type: {type(stop)}")
                logger.debug(
                    f"Stop {i} keys: {list(stop.keys()) if isinstance(stop, dict) else 'Not a dict'}"
                )

                # Extract destination information if available
                destination_name = None
                line_number = None
                platform = None

                if isinstance(stop, dict):
                    # Extract line number from transportation.disassembledName
                    if "transportation" in stop:
                        transportation = stop.get("transportation", {})
                        logger.debug(f"Transportation data: {transportation}")
                        if isinstance(transportation, dict):
                            line_number = transportation.get("disassembledName")
                            logger.debug(f"Extracted line: {line_number}")

                            # Extract destination from transportation.destination.name
                            destination = transportation.get("destination", {})
                            logger.debug(f"Destination data: {destination}")
                            if isinstance(destination, dict):
                                destination_name = destination.get("name")
                                logger.debug(
                                    f"Extracted destination: {destination_name}"
                                )

                    # Extract platform from location.properties.platform
                    if "location" in stop:
                        location = stop.get("location", {})
                        logger.debug(f"Location data: {location}")
                        if isinstance(location, dict):
                            properties = location.get("properties", {})
                            if isinstance(properties, dict):
                                platform = properties.get("platform")
                                logger.debug(f"Extracted platform: {platform}")

                    # Also check if destination is directly in the stop object
                    if not destination_name and "destination" in stop:
                        direct_dest = stop.get("destination", {})
                        logger.debug(f"Direct destination data: {direct_dest}")
                        if isinstance(direct_dest, dict):
                            destination_name = direct_dest.get("name")
                            logger.debug(
                                f"Extracted direct destination: {destination_name}"
                            )

                journey_stop = JourneyStop(
                    name=stop.get("name", ""),
                    departure_time=stop.get("departure_time"),
                    minutes_from_now=stop.get("minutes_from_now"),
                    transport_mode=stop.get("transport_mode", ""),
                    line=line_number
                    or stop.get("line", ""),  # Use extracted line number
                    is_realtime=stop.get("is_realtime", False),
                    destination_name=destination_name,
                    platform=platform,
                    id=stop.get("id"),  # Include stop ID
                    arrival_time=stop.get("arrival_time"),
                )

                # Calculate arrival time in minutes for destination stops
                if (
                    journey_stop.is_destination_stop(self.config.destination_stop_id)
                    and journey_stop.minutes_from_now is None
                    and journey_stop.arrival_time
                ):
                    try:
                        from datetime import datetime

                        arr_time = datetime.fromisoformat(
                            journey_stop.arrival_time.replace("Z", "+00:00")
                        )
                        current_time = datetime.now(arr_time.tzinfo)
                        time_diff = arr_time - current_time
                        journey_stop.minutes_from_now = int(
                            time_diff.total_seconds() / 60
                        )
                    except Exception as e:
                        logger.warning(
                            f"Failed to calculate arrival minutes for destination stop {journey_stop.clean_name}: {e}"
                        )

                journey_stops.append(journey_stop)
                logger.debug(
                    f"Created JourneyStop: {journey_stop.clean_name} - Line: {journey_stop.line} ({journey_stop.line_number}) - Destination: {journey_stop.destination_name} - Platform: {journey_stop.platform_number}"
                )
                logger.debug(
                    f"Destination primary: '{journey_stop.destination_primary}', via: '{journey_stop.destination_via}'"
                )

            # Filter valid stops and include destination stops
            valid_stops = [
                stop
                for stop in journey_stops
                if stop.is_valid()
                or stop.is_destination_stop(self.config.destination_stop_id)
            ]

            logger.info(
                f"Retrieved {len(valid_stops)} valid stops from {len(journey_stops)} total"
            )

            return valid_stops[: self.config.max_stops_display]

        except Exception as e:
            logger.error(f"Error fetching journey stops: {e}")
            return []
