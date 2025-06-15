#!/usr/bin/python3
"""
Test script to debug import issues on Raspberry Pi
"""

import sys
import os

print("=== Import Test Script ===")
print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")
print(f"Script location: {os.path.dirname(os.path.realpath(__file__))}")

# Check if lib directory exists
script_dir = os.path.dirname(os.path.realpath(__file__))
libdir = os.path.join(script_dir, "lib")
print(f"Lib directory path: {libdir}")
print(f"Lib directory exists: {os.path.exists(libdir)}")

if os.path.exists(libdir):
    print("Lib directory contents:")
    for item in os.listdir(libdir):
        print(f"  - {item}")

    # Add to path
    sys.path.insert(0, libdir)
    print(f"Added {libdir} to sys.path")
    print(f"sys.path: {sys.path}")

    # Try to import
    try:
        print("\nTrying to import display_factory...")
        from display_factory import DisplayFactory

        print("✓ Successfully imported DisplayFactory")

        print("\nTrying to import display_interface...")
        from display_interface import DisplayInterface

        print("✓ Successfully imported DisplayInterface")

        print("\nTrying to import hardware_display...")
        from hardware_display import HardwareDisplay

        print("✓ Successfully imported HardwareDisplay")

        print("\nTrying to import simulation_display...")
        from simulation_display import SimulationDisplay

        print("✓ Successfully imported SimulationDisplay")

        print("\n=== All imports successful! ===")

    except ImportError as e:
        print(f"✗ Import failed: {e}")
        print(f"Current sys.path: {sys.path}")
else:
    print("✗ Lib directory not found!")
