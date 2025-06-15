#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
Live Clock Application
Displays a real-time clock on the e-paper display that updates every minute
"""

import sys
import os
import time
import threading
from datetime import datetime

# Add the lib directory to the path
script_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
libdir = os.path.join(script_dir, "lib")
sys.path.insert(0, libdir)

from display_factory import DisplayFactory
from time_display import TimeDisplay


class LiveClock:
    """Live clock application that updates the display in real-time"""

    def __init__(self, simulate=True, width=800, height=480, update_interval=60):
        """
        Initialize the live clock

        Args:
            simulate: Whether to use simulation mode
            width: Display width
            height: Display height
            update_interval: Update interval in seconds (default: 60 for every minute)
        """
        self.simulate = simulate
        self.width = width
        self.height = height
        self.update_interval = update_interval
        self.running = False

        # Create display
        self.display = DisplayFactory.create_display(
            simulate=simulate, width=width, height=height
        )

        # Create time display
        self.time_display = TimeDisplay(font_size=72)

        # Initialize display
        self.display.init()
        self.display.clear()

    def start(self):
        """Start the live clock"""
        self.running = True

        print("Live Clock Started!")
        print("Press Ctrl+C to exit")
        print()

        # Run clock in main thread for simulation
        self._run_clock()

    def stop(self):
        """Stop the live clock"""
        self.running = False
        print("\nStopping live clock...")
        self.display.clear()
        if not self.simulate:
            self.display.sleep()
        else:
            self.display.run()

    def _run_clock(self):
        """Main clock loop that updates every minute"""
        last_minute = -1

        while self.running:
            try:
                current_time = datetime.now()
                current_minute = current_time.minute

                # Always update on first run or when minute changes
                if last_minute == -1 or current_minute != last_minute:
                    time_str = current_time.strftime("%H:%M:%S")
                    date_str = current_time.strftime("%Y-%m-%d")
                    weekday_str = current_time.strftime("%A")

                    print(f"Updating display: {time_str} - {weekday_str}, {date_str}")

                    # Create new clock image
                    clock_image = self.time_display.create_clock_image(
                        self.width, self.height, show_seconds=True
                    )

                    # Display the clock
                    self.display.display(clock_image)

                    last_minute = current_minute

                # Wait for next update (check every second)
                time.sleep(1)

            except KeyboardInterrupt:
                print("\nInterrupted by user")
                break
            except Exception as e:
                print(f"Error updating clock: {e}")
                time.sleep(5)  # Wait a bit longer on error

    def show_digital_time(self):
        """Show digital time display that updates every minute"""
        self.running = True
        last_minute = -1

        print("Digital Time Display Started!")
        print("Press Ctrl+C to exit")
        print()

        while self.running:
            try:
                current_time = datetime.now()
                current_minute = current_time.minute

                # Update when minute changes
                if last_minute == -1 or current_minute != last_minute:
                    time_str = current_time.strftime("%H:%M:%S")
                    date_str = current_time.strftime("%Y-%m-%d")
                    weekday_str = current_time.strftime("%A")

                    print(f"Updating display: {time_str} - {weekday_str}, {date_str}")

                    time_image = self.time_display.create_time_image(
                        self.width, self.height, show_date=True, show_weekday=True
                    )
                    self.display.display(time_image)

                    last_minute = current_minute

                # Wait for next update
                time.sleep(1)

            except KeyboardInterrupt:
                print("\nInterrupted by user")
                break
            except Exception as e:
                print(f"Error updating time: {e}")
                time.sleep(5)

        self.stop()


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="Live Clock Application")
    parser.add_argument(
        "--simulate",
        action="store_true",
        help="Run in simulation mode",
    )
    parser.add_argument(
        "--digital",
        action="store_true",
        help="Show digital time instead of analog clock",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=800,
        help="Display width (default: 800)",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=480,
        help="Display height (default: 480)",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Update interval in seconds (default: 60)",
    )

    args = parser.parse_args()

    print("Live Clock Application")
    print("=====================")
    print(f"Mode: {'Simulation' if args.simulate else 'Hardware'}")
    print(f"Display: {args.width}x{args.height}")
    print(f"Update Interval: {args.interval} seconds")
    print(f"Display Type: {'Digital' if args.digital else 'Analog Clock'}")
    print()

    # Create and start clock
    clock = LiveClock(
        simulate=args.simulate,
        width=args.width,
        height=args.height,
        update_interval=args.interval,
    )

    if args.digital:
        clock.show_digital_time()
    else:
        clock.start()


if __name__ == "__main__":
    main()
