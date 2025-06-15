#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
Test Runner
Runs all tests in the tests directory
"""

import sys
import os
import subprocess
import importlib.util

# Add the lib directory to the path
script_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
libdir = os.path.join(script_dir, "lib")
sys.path.insert(0, libdir)


def run_test_file(test_file):
    """Run a single test file"""
    print(f"\n{'='*50}")
    print(f"Running: {test_file}")
    print(f"{'='*50}")

    try:
        result = subprocess.run(
            [sys.executable, test_file], capture_output=True, text=True, timeout=30
        )

        if result.returncode == 0:
            print("✅ Test passed")
            print(result.stdout)
        else:
            print("❌ Test failed")
            print(result.stdout)
            print(result.stderr)

        return result.returncode == 0

    except subprocess.TimeoutExpired:
        print("⏰ Test timed out")
        return False
    except Exception as e:
        print(f"❌ Error running test: {e}")
        return False


def main():
    """Run all tests"""

    print("E-Paper Display Test Suite")
    print("==========================")
    print()

    # Get all test files
    test_dir = os.path.dirname(os.path.realpath(__file__))
    test_files = [
        f for f in os.listdir(test_dir) if f.startswith("test_") and f.endswith(".py")
    ]

    test_files.sort()  # Run in alphabetical order

    print(f"Found {len(test_files)} test files:")
    for test_file in test_files:
        print(f"  - {test_file}")
    print()

    # Run tests
    passed = 0
    failed = 0

    for test_file in test_files:
        test_path = os.path.join(test_dir, test_file)
        if run_test_file(test_path):
            passed += 1
        else:
            failed += 1

    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print(f"{'='*50}")
    print(f"Total tests: {len(test_files)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed == 0:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n❌ {failed} test(s) failed")

    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
