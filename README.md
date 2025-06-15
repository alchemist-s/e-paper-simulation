# E-Paper Display Controller

A Python library for controlling e-paper displays with support for both hardware and simulation modes. This project provides a clean, object-oriented interface for working with various e-paper display types.

## Features

- **Hardware Support**: Direct control of e-paper displays via SPI
- **Simulation Mode**: Test your code without physical hardware using Tkinter or file output
- **Time Display**: Real-time clock and date display functionality
- **Modular Design**: Clean separation between display interface and implementations
- **Cross-Platform**: Works on Raspberry Pi, desktop computers, and other platforms
- **Flexible**: Easy to extend for new display types

## Installation

1. Clone this repository:

```bash
git clone <your-repo-url>
cd e-paper-main
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from lib.display_factory import DisplayFactory

# For hardware mode (requires physical e-paper display)
from waveshare_epd import epd7in5b_V2
display = DisplayFactory.create_display(simulate=False, epd_module=epd7in5b_V2)

# For simulation mode
display = DisplayFactory.create_display(simulate=True, width=800, height=480)

# Initialize and clear display
display.init()
display.clear()

# Display images
from PIL import Image
image = Image.new('1', (display.width, display.height), 255)
display.display(image)
```

### Time Display Usage

```python
from lib.time_display import TimeDisplay

# Create time display
time_display = TimeDisplay(font_size=64)

# Show digital time
time_image = time_display.create_time_image(800, 480, show_date=True, show_weekday=True)
display.display(time_image)

# Show analog clock
clock_image = time_display.create_clock_image(800, 480, show_seconds=True)
display.display(clock_image)
```

### Command Line Usage

```bash
# Run with hardware display
python3 main.py

# Run in simulation mode
python3 main.py --simulate

# Show clock display
python3 main.py --clock

# Run live clock
python3 examples/live_clock.py --simulate
```

## Project Structure

```
e-paper-main/
├── lib/                    # Core library files
│   ├── display_interface.py    # Abstract base class
│   ├── display_factory.py      # Factory for creating displays
│   ├── hardware_display.py     # Hardware implementation
│   ├── simulation_display.py   # Simulation implementation
│   └── time_display.py         # Time display functionality
├── examples/               # Example applications
│   ├── live_clock.py          # Real-time clock application
│   └── time_example.py        # Time display examples
├── tests/                  # Test files
│   ├── run_tests.py           # Test runner
│   ├── test_hardware_mode.py  # Hardware mode tests
│   ├── test_hardware_fix.py   # Display fix tests
│   ├── test_realtime.py       # Real-time tests
│   └── test_imports.py        # Import tests
├── main.py                 # Main demo script
├── pic/                    # Image assets
└── requirements.txt        # Dependencies
```

## Display Modes

### Hardware Mode

- Controls physical e-paper displays
- Requires appropriate hardware drivers
- Real-time display updates
- Power-efficient for e-paper displays

### Simulation Mode

- **Tkinter**: Real-time window display (when available)
- **File Output**: Saves images to `simulation_output/` directory
- Perfect for testing and development
- No hardware required

## Time Display Features

### Digital Time Display

- Current time (HH:MM:SS)
- Current date (YYYY-MM-DD)
- Current weekday
- Centered layout with configurable fonts

### Analog Clock Display

- Traditional clock face with hour markers
- Hour, minute, and second hands
- Option to show/hide seconds
- Automatically sized for display

### Real-time Updates

- Updates every minute (configurable)
- Works in both simulation and hardware modes
- Power-efficient for e-paper displays

## Supported Displays

This library is designed to work with various e-paper display types. The current implementation supports:

- 7.5" e-paper displays (tested)
- Extensible for other sizes and types

## Testing

### Run All Tests

```bash
python3 tests/run_tests.py
```

### Run Individual Tests

```bash
# Test hardware mode
python3 tests/test_hardware_mode.py

# Test real-time functionality
python3 tests/test_realtime.py

# Test imports
python3 tests/test_imports.py
```

## Development

### Adding New Display Types

1. Create a new display class implementing `DisplayInterface`
2. Add it to the `DisplayFactory`
3. Update documentation

### Adding New Tests

1. Create a file starting with `test_` in the `tests/` directory
2. Follow the import pattern used in existing tests
3. The test runner will automatically pick up your new test

## Troubleshooting

### Common Issues

1. **ImportError: cannot import name 'ImageTk'**

   - This is normal on systems without Tkinter support
   - The simulation will automatically fall back to file output

2. **Hardware not detected**

   - Ensure proper SPI configuration
   - Check hardware connections
   - Verify driver installation

3. **Permission errors on Raspberry Pi**

   - Run with appropriate permissions for SPI access
   - Consider using `sudo` for hardware access

4. **"epd_module is required for hardware mode"**
   - Use `--simulate` flag for testing on non-Raspberry Pi systems
   - Ensure waveshare_epd module is available for hardware mode

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Based on Waveshare e-paper display libraries
- Inspired by the need for better testing and simulation capabilities
