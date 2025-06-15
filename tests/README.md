# Tests Directory

This directory contains all test files for the e-paper display project.

## Test Files

### `test_hardware_mode.py`

Tests hardware and simulation mode functionality.

- Verifies e-paper module import
- Tests hardware display creation
- Tests simulation display creation
- Provides environment status

### `test_hardware_fix.py`

Tests the hardware display fix for single images.

- Tests single image display (creates blank red image automatically)
- Tests double image display (works as before)
- Verifies the fix for the "missing imagered argument" error

### `test_realtime.py`

Quick real-time test for time display functionality.

- Shows 5 time updates at 2-second intervals
- Demonstrates real-time updates in simulation mode
- Tests time display image creation and display

### `test_imports.py`

Tests import functionality for debugging.

- Tests all module imports
- Shows Python version and paths
- Useful for debugging import issues on Raspberry Pi

### `run_tests.py`

Test runner script that executes all tests.

- Runs all test files automatically
- Provides summary of results
- Can be used for CI/CD integration

## Running Tests

### Run All Tests

```bash
python3 tests/run_tests.py
```

### Run Individual Tests

```bash
# Test hardware mode
python3 tests/test_hardware_mode.py

# Test hardware display fix
python3 tests/test_hardware_fix.py

# Test real-time functionality
python3 tests/test_realtime.py

# Test imports
python3 tests/test_imports.py
```

## Expected Results

### On macOS/Linux (without e-paper hardware)

- `test_hardware_mode.py`: Simulation mode works, hardware mode fails (expected)
- `test_hardware_fix.py`: Both single and double image tests pass
- `test_realtime.py`: Shows real-time updates in Tkinter window
- `test_imports.py`: All imports successful

### On Raspberry Pi (with e-paper hardware)

- `test_hardware_mode.py`: Both simulation and hardware modes work
- `test_hardware_fix.py`: Both single and double image tests pass
- `test_realtime.py`: Shows real-time updates in Tkinter window
- `test_imports.py`: All imports successful

## Test Categories

### ✅ **Unit Tests**

- Import functionality
- Display creation
- Image handling

### ✅ **Integration Tests**

- Hardware mode integration
- Simulation mode integration
- Time display functionality

### ✅ **Functional Tests**

- Real-time updates
- Single/double image display
- Error handling

## Adding New Tests

To add a new test:

1. Create a file starting with `test_` in the `tests/` directory
2. Follow the import pattern used in existing tests:

   ```python
   import sys
   import os

   # Add the lib directory to the path
   script_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
   libdir = os.path.join(script_dir, "lib")
   sys.path.insert(0, libdir)

   from display_factory import DisplayFactory
   # ... other imports
   ```

3. The test runner will automatically pick up your new test

## Continuous Integration

The test runner (`run_tests.py`) is designed to work with CI/CD systems:

- Returns exit code 0 for success, 1 for failure
- Provides clear output for logging
- Handles timeouts and errors gracefully

## Troubleshooting

### Import Errors

If you get import errors when running tests:

1. Ensure you're running from the project root directory
2. Check that the `lib/` directory exists
3. Run `python3 tests/test_imports.py` to debug import issues

### Test Failures

- Hardware tests may fail on non-Raspberry Pi systems (expected)
- Simulation tests should always pass
- Check console output for specific error messages

The tests provide comprehensive coverage of the e-paper display functionality and help ensure reliability across different environments.
