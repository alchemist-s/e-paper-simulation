#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
Transport Display System
Displays journey stops from Rhodes to Central on e-paper display
Supports both hardware and simulation modes with partial updates for time display
"""

import sys
import argparse
import logging

from .journey_display import JourneyDisplay
from .utils import get_api_key

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main() -> int:
    """Main function"""
    parser = argparse.ArgumentParser(description="Transport Display System")
    parser.add_argument(
        "--simulate",
        action="store_true",
        help="Run in simulation mode (default: hardware mode)",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run in demo mode with limited duration (default: continuous mode)",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=300,
        help="Duration to run the demo in seconds (default: 300, only used with --demo)",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument(
        "--epd-module",
        type=str,
        help="Specify e-paper module to use (default: epd7in5b_V2)",
    )
    parser.add_argument(
        "--test-partial",
        action="store_true",
        help="Test partial updates only (for development)",
    )

    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Determine mode
    mode = "Simulation" if args.simulate else "Hardware"
    run_mode = "Demo" if args.demo else "Continuous"

    print("Transport Display System")
    print("========================")
    print(f"Mode: {mode}")
    print(f"Run Mode: {run_mode}")
    if args.demo:
        print(f"Duration: {args.duration} seconds")
    if args.test_partial:
        print("Partial Update Testing: Enabled")
    print()

    try:
        # Get API key
        api_key = get_api_key()

        # Determine e-paper module
        epd_module = None
        if not args.simulate and args.epd_module:
            try:
                # Dynamic import of the specified module
                import importlib

                waveshare_epd = importlib.import_module("waveshare_epd")
                epd_module = getattr(waveshare_epd, args.epd_module)
                logger.info(f"Using specified e-paper module: {args.epd_module}")
            except ImportError:
                logger.error(
                    f"Failed to import e-paper module '{args.epd_module}': {e}"
                )
                return 1

        # Initialize display
        display = JourneyDisplay(api_key, simulate=args.simulate, epd_module=epd_module)

        # Initialize and clear display
        init_result = display.display.init()
        if init_result != 0:
            logger.error("Failed to initialize display")
            return 1

        display.display.clear()

        # Run the appropriate mode
        if args.test_partial:
            # Test partial updates
            logger.info("Testing partial updates...")
            display.update_display(force_full_update=True)  # Initial full update
            import time

            for i in range(5):
                time.sleep(60)  # Wait 1 minute
                display.update_display(force_full_update=False)  # Partial update
                logger.info(f"Partial update test {i+1}/5 completed")
        elif args.demo:
            display.run_demo(duration=args.duration)
        else:
            display.run_continuous()

        # Cleanup
        display.display.sleep()

        print("\nTransport display completed!")
        if args.simulate:
            print("Check the generated PNG files to see the journey display states.")
        print(f"Total updates: {display.display.update_count}")

        return 0

    except Exception as e:
        logger.error(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
