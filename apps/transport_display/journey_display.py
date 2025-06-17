#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
Main journey display controller
"""

import time
import logging
from datetime import datetime

from .models import DisplayConfig, JourneyConfig
from .journey_data_service import JourneyDataService
from .display_renderer import DisplayRenderer
from .hardware_display_manager import HardwareDisplayManager
from .partial_updater import PartialUpdater

logger = logging.getLogger(__name__)


class JourneyDisplay:
    """Main journey display controller"""

    def __init__(self, api_key: str, simulate: bool = False, epd_module=None):
        self.display_config = DisplayConfig()
        self.journey_config = JourneyConfig()

        # Use hardware display manager instead of mock
        self.display = HardwareDisplayManager(
            self.display_config, simulate=simulate, epd_module=epd_module
        )
        self.data_service = JourneyDataService(api_key, self.journey_config)
        self.renderer = DisplayRenderer(self.display_config)
        self.partial_updater = PartialUpdater(self.display_config)

        # Track state for partial updates
        self.last_journey_data = None
        self.last_banner_time = None
        self.last_service_time = None
        self.current_stops = None

    def fetch_journey_data(self) -> None:
        """Fetch journey data from API"""
        logger.info("Fetching journey data from API...")
        self.current_stops = self.data_service.get_journey_stops()

        # Log what we fetched
        if self.current_stops:
            logger.info(f"Fetched {len(self.current_stops)} stops")
            for stop in self.current_stops[:3]:
                logger.info(f"  {stop.clean_name} - {stop.time_display}")
        else:
            logger.info("No journey data available")

    def update_display(self, force_full_update: bool = False) -> None:
        """Update the journey display"""
        current_time = datetime.now().strftime("%H:%M")

        # Check if we need a full update (new journey data)
        needs_full_update = force_full_update or (
            self.last_journey_data is None
            or self.current_stops is None
            or len(self.current_stops) != len(self.last_journey_data)
            or (
                self.current_stops
                and self.last_journey_data
                and self.current_stops[0].minutes_from_now
                != self.last_journey_data[0].minutes_from_now
            )
        )

        if needs_full_update:
            # Full update for new journey data
            logger.info("Performing full display update (journey data changed)")
            self._perform_full_update(self.current_stops)
            self.last_journey_data = (
                self.current_stops.copy() if self.current_stops else None
            )
        else:
            # Partial updates for time changes only
            logger.info("Performing partial time updates")
            self._perform_partial_time_updates(self.current_stops, current_time)

    def _perform_full_update(self, stops) -> None:
        """Perform a full display update"""
        # Create and update display
        display_image = self.renderer.create_journey_display(stops)
        self.display.update_display(display_image)

    def _perform_partial_time_updates(self, stops, current_time: str) -> None:
        """Perform partial updates for time changes only"""
        # Update banner time if changed
        if current_time != self.last_banner_time:
            logger.debug(f"Updating banner time: {current_time}")
            banner_image, banner_region = (
                self.partial_updater.create_banner_time_update(current_time)
            )
            self.display.update_partial(banner_image, banner_region)
            self.last_banner_time = current_time

        # Update next service time if changed
        if stops and stops[0].time_display != self.last_service_time:
            logger.debug(f"Updating service time: {stops[0].time_display}")
            service_image, service_region = (
                self.partial_updater.create_next_service_time_update(stops[0])
            )
            self.display.update_partial(service_image, service_region)
            self.last_service_time = stops[0].time_display

    def run_demo(self, duration: int = 300) -> None:
        """Run the journey display demo"""
        mode = "SIMULATION" if self.display.simulate else "HARDWARE"
        logger.info(f"Starting journey display demo ({mode} MODE)...")
        logger.info("Will show journey stops from Rhodes to Central")
        logger.info("Press Ctrl+C to stop early")

        start_time = time.time()
        last_data_fetch = 0
        last_time_update = 0

        try:
            while time.time() - start_time < duration:
                current_time = time.time()

                # Fetch new journey data every journey_config.update_interval seconds
                if (
                    current_time - last_data_fetch
                    >= self.journey_config.update_interval
                ):
                    self.fetch_journey_data()
                    self.update_display(force_full_update=True)
                    last_data_fetch = current_time
                    logger.info(
                        f"Next data fetch in {self.journey_config.update_interval} seconds"
                    )

                # Partial time updates every minute (without fetching new data)
                elif current_time - last_time_update >= 60:
                    self.update_display(force_full_update=False)
                    last_time_update = current_time
                    logger.debug("Time update completed")

                time.sleep(1)

        except KeyboardInterrupt:
            logger.info("Demo stopped by user")

        logger.info("Journey demo completed!")
        logger.info(f"Total updates: {self.display.update_count}")

    def run_continuous(self) -> None:
        """Run the journey display continuously (for production use)"""
        mode = "SIMULATION" if self.display.simulate else "HARDWARE"
        logger.info(f"Starting continuous journey display ({mode} MODE)...")
        logger.info("Will update every 60 seconds. Press Ctrl+C to stop.")

        last_data_fetch = 0
        last_time_update = 0

        try:
            while True:
                current_time = time.time()

                # Fetch new journey data every journey_config.update_interval seconds
                if (
                    current_time - last_data_fetch
                    >= self.journey_config.update_interval
                ):
                    self.fetch_journey_data()
                    self.update_display(force_full_update=True)
                    last_data_fetch = current_time
                    logger.info(
                        f"Next data fetch in {self.journey_config.update_interval} seconds"
                    )

                # Partial time updates every minute (without fetching new data)
                elif current_time - last_time_update >= 60:
                    self.update_display(force_full_update=False)
                    last_time_update = current_time
                    logger.debug("Time update completed")

                time.sleep(1)

        except KeyboardInterrupt:
            logger.info("Continuous display stopped by user")

        logger.info("Continuous display completed!")
        logger.info(f"Total updates: {self.display.update_count}")
