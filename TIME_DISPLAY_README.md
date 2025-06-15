# Time Display Functionality

This document describes the time display features added to the e-paper display project.

## Overview

The time display functionality provides real-time clock and date display capabilities for e-paper displays. It includes both digital and analog clock displays that can update in real-time.

## Features

### 1. Digital Time Display

- Shows current time in HH:MM:SS format
- Displays current date (YYYY-MM-DD)
- Shows current weekday
- Centered text layout
- Configurable font sizes

### 2. Analog Clock Display

- Traditional clock face with hour markers
- Hour, minute, and second hands
- Option to show/hide second hand
- Automatically sized for display

### 3. Real-time Updates

- Updates every minute (configurable)
- Works in both simulation and hardware modes
- Proper Tkinter integration for simulation

## Files Added

### Core Module

- `lib/time_display.py` - Main TimeDisplay class

### Example Applications

- `examples/time_example.py` - Basic time display examples
- `examples/live_clock.py` - Real-time updating clock
- `examples/realtime_demo.py` - Demo with frequent updates
- `examples/simple_realtime_test.py` - Simple test script
- `test_realtime.py` - Quick test script

### Modified Files

- `main.py` - Added time display to main demo

## Usage

### Basic Time Display

```python
from lib.time_display import TimeDisplay
from lib.display_factory import DisplayFactory

# Create display
display = DisplayFactory.create_display(simulate=True, width=800, height=480)
display.init()
display.clear()

# Create time display
time_display = TimeDisplay(font_size=64)

# Show digital time
time_image = time_display.create_time_image(
    display.width, display.height,
    show_date=True, show_weekday=True
)
display.display(time_image)

# Show analog clock
clock_image = time_display.create_clock_image(
    display.width, display.height,
    show_seconds=True
)
display.display(clock_image)
```

### Command Line Usage

```bash
# Show clock display only
python3 main.py --simulate --clock

# Run regular demo with time display
python3 main.py --simulate

# Run time display examples
python3 examples/time_example.py

# Run live clock (updates every minute)
python3 examples/live_clock.py --simulate

# Run live clock with digital display
python3 examples/live_clock.py --simulate --digital

# Quick real-time test
python3 test_realtime.py
```

### Live Clock Application

The live clock application provides continuous time updates:

```bash
# Analog clock (updates every minute)
python3 examples/live_clock.py --simulate

# Digital clock (updates every minute)
python3 examples/live_clock.py --simulate --digital

# Custom update interval (e.g., every 30 seconds)
python3 examples/live_clock.py --simulate --interval 30
```

## Configuration Options

### TimeDisplay Class

```python
time_display = TimeDisplay(
    font_path="path/to/font.ttc",  # Optional custom font
    font_size=64                   # Font size for time display
)
```

### Digital Time Display

```python
time_image = time_display.create_time_image(
    width=800,           # Display width
    height=480,          # Display height
    show_date=True,      # Show date
    show_weekday=True    # Show weekday
)
```

### Analog Clock Display

```python
clock_image = time_display.create_clock_image(
    width=800,           # Display width
    height=480,          # Display height
    show_seconds=True    # Show second hand
)
```

## Real-time Updates

The time display can update in real-time:

### In Simulation Mode

- Updates are visible in the Tkinter window
- Window refreshes automatically
- Can see time changing every minute

### In Hardware Mode

- Updates are sent to the e-paper display
- Display refreshes every minute
- Power-efficient for e-paper displays

## Testing

### Quick Test

```bash
python3 test_realtime.py
```

This shows 5 time updates at 2-second intervals.

### Simple Test

```bash
python3 examples/simple_realtime_test.py
```

This shows 10 time updates at 3-second intervals.

### Live Clock Test

```bash
python3 examples/live_clock.py --simulate --digital
```

This runs a continuous digital clock that updates every minute.

## Integration with Main Demo

The main demo now includes time display:

1. Original demo content
2. **NEW**: Time display section
3. BMP file display

Use `--clock` flag to show only the clock display.

## Font Support

- Uses custom font if available (`pic/Font.ttc`)
- Falls back to default system font
- Configurable font sizes
- Automatic text centering

## Error Handling

- Graceful font loading fallback
- Tkinter availability checking
- Exception handling for display updates
- Keyboard interrupt support

## Performance Considerations

### E-paper Displays

- Updates every minute (not every second) to preserve display life
- Minimal power consumption
- Proper sleep/wake cycles

### Simulation Mode

- Real-time updates visible
- Tkinter window refreshes
- Configurable update intervals

## Future Enhancements

Potential improvements:

- Weather integration
- Multiple time zones
- Custom time formats
- Alarm functionality
- Calendar integration
- Network time synchronization

## Troubleshooting

### Common Issues

1. **Font not found**: Uses default font automatically
2. **Tkinter errors**: Falls back to file output
3. **Display not updating**: Check update intervals
4. **Window not showing**: Ensure simulation mode is enabled

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Examples

See the `examples/` directory for complete working examples:

- `time_example.py` - Basic functionality
- `live_clock.py` - Real-time clock
- `realtime_demo.py` - Demo with frequent updates
- `simple_realtime_test.py` - Simple test

The time display functionality provides a solid foundation for building time-based applications on e-paper displays!
