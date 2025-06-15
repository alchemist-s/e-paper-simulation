#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
Module Composition Example
Demonstrates how to compose multiple modules into a single view
"""

import sys
import os
import time
import argparse

# Add the lib directory to the path
script_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
libdir = os.path.join(script_dir, "lib")
sys.path.insert(0, libdir)

from display_factory import DisplayFactory
from module_interface import ModuleContainer
from modules.time_module import TimeModule
from modules.text_module import TextModule


def create_clock_view():
    """Create a view with just a clock"""
    container = ModuleContainer(width=800, height=480)

    # Add a large analog clock with 1-second refresh interval
    clock_module = TimeModule(
        mode="analog",
        font_size=72,
        show_seconds=True,
        refresh_interval=1,  # update every second
    )

    container.add_module(clock_module, {"x": 0, "y": 0, "width": 800, "height": 480})

    return container


def create_dashboard_view():
    """Create a dashboard view with multiple modules"""
    container = ModuleContainer(width=800, height=480)

    # Add title at the top
    title_module = TextModule(
        text="E-Paper Dashboard", font_size=32, align="center", valign="top"
    )

    container.add_module(title_module, {"x": 0, "y": 10, "width": 800, "height": 50})

    # Add digital time on the left
    time_module = TimeModule(
        mode="digital",
        font_size=48,
        show_date=True,
        show_weekday=True,
        refresh_interval=1,
    )

    container.add_module(time_module, {"x": 50, "y": 100, "width": 300, "height": 200})

    # Add status text on the right
    status_module = TextModule(
        text="System Online\nAll systems operational\nLast update: Now",
        font_size=24,
        align="left",
        valign="top",
    )

    container.add_module(
        status_module, {"x": 450, "y": 100, "width": 300, "height": 200}
    )

    # Add footer text
    footer_module = TextModule(
        text="E-Paper Display System v1.0",
        font_size=16,
        align="center",
        valign="bottom",
    )

    container.add_module(footer_module, {"x": 0, "y": 430, "width": 800, "height": 50})

    return container


def create_split_view():
    """Create a split view with time and text"""
    container = ModuleContainer(width=800, height=480)

    # Left side - analog clock
    clock_module = TimeModule(
        mode="analog",
        font_size=64,
        show_seconds=True,
        refresh_interval=1,  # update every second
    )

    container.add_module(clock_module, {"x": 0, "y": 0, "width": 400, "height": 480})

    # Right side - digital time and info
    digital_module = TimeModule(
        mode="digital",
        font_size=36,
        show_date=True,
        show_weekday=True,
        refresh_interval=1,  # update every second
    )

    container.add_module(
        digital_module, {"x": 400, "y": 50, "width": 400, "height": 150}
    )

    # Info text below digital time
    info_module = TextModule(
        text="Current Status:\n• System Running\n• Display Active\n• Time Synced",
        font_size=20,
        align="left",
        valign="top",
    )

    container.add_module(info_module, {"x": 400, "y": 220, "width": 400, "height": 200})

    return container


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Module Composition Example")
    parser.add_argument(
        "--simulate",
        action="store_true",
        help="Run in simulation mode",
    )
    parser.add_argument(
        "--view",
        choices=["clock", "dashboard", "split"],
        default="dashboard",
        help="View to display (default: dashboard)",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Run in live mode with updates",
    )

    args = parser.parse_args()

    print("Module Composition Example")
    print("=========================")
    print(f"View: {args.view}")
    print(f"Mode: {'Simulation' if args.simulate else 'Hardware'}")
    print(f"Live: {'Yes' if args.live else 'No'}")
    print()

    # Create display
    if args.simulate:
        display = DisplayFactory.create_display(simulate=True, width=800, height=480)
    else:
        # Import e-paper module for hardware mode
        try:
            from waveshare_epd import epd7in5b_V2

            display = DisplayFactory.create_display(
                simulate=False, epd_module=epd7in5b_V2
            )
        except ImportError as e:
            print(f"Error importing e-paper module: {e}")
            print(
                "Please ensure the waveshare_epd module is available for hardware mode."
            )
            print("Or use --simulate flag to run in simulation mode.")
            sys.exit(1)

    # Initialize display
    display.init()
    display.clear()

    # Create the appropriate view
    if args.view == "clock":
        container = create_clock_view()
    elif args.view == "dashboard":
        container = create_dashboard_view()
    elif args.view == "split":
        container = create_split_view()

    if args.live:
        # Live mode - update every second (dynamic updates)
        print("Running in live mode. Press Ctrl+C to exit.")
        print()

        if args.simulate:
            # Use Tkinter's after() for periodic updates in simulation mode
            def update_sim():
                image = container.render()
                display.display(image)
                display.root.after(1000, update_sim)

            # Initial render and start loop
            update_sim()
            display.run()
        else:
            try:
                import time

                while True:
                    # Render the view (only modules needing update will be re-rendered)
                    image = container.render()
                    display.display(image)
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nStopping live mode...")
    else:
        # Single display
        print("Rendering view...")

        # Render the view
        image = container.render()

        # Display the image
        display.display(image)

        print("View displayed!")

        if args.simulate:
            # Keep window open in simulation mode
            display.run()


if __name__ == "__main__":
    main()
