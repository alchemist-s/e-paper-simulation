# E-Paper Display Controller

A Python library for controlling e-paper displays with support for both hardware and simulation modes. This project provides a clean, object-oriented interface for working with various e-paper display types.

## Features

- **Hardware Support**: Direct control of e-paper displays via SPI
- **Simulation Mode**: Test your code without physical hardware using Tkinter or file output
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

### Command Line Usage

```bash
# Run with hardware display
python3 main.py

# Run in simulation mode (saves images to files)
python3 main.py --simulate
```

## Project Structure

```
e-paper-main/
├── lib/                    # Core library files
│   ├── display_interface.py    # Abstract base class
│   ├── display_factory.py      # Factory for creating displays
│   ├── hardware_display.py     # Hardware implementation
│   └── simulation_display.py   # Simulation implementation
├── main.py                 # Main demo script
├── examples/               # Example code
├── pic/                    # Image assets
└── setup.py               # Package setup
```

## Display Modes

### Hardware Mode

- Controls physical e-paper displays
- Requires appropriate hardware drivers
- Real-time display updates

### Simulation Mode

- **Tkinter**: Real-time window display (when available)
- **File Output**: Saves images to `simulation_output/` directory
- Perfect for testing and development

## Supported Displays

This library is designed to work with various e-paper display types. The current implementation supports:

- 7.5" e-paper displays (tested)
- Extensible for other sizes and types

## Development

### Adding New Display Types

1. Create a new display class implementing `DisplayInterface`
2. Add it to the `DisplayFactory`
3. Update documentation

### Testing

```bash
# Test in simulation mode
python3 main.py --simulate

# Check generated images in simulation_output/
ls simulation_output/
```

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
