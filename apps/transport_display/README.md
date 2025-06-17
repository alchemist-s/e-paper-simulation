# Transport Display System

A complete transport journey display system for e-paper displays. Shows real-time journey information from Rhodes to Central using the Transport NSW API. Supports both hardware e-paper displays and simulation mode with optimized partial updates.

## Features

- **Real-time Transport Data**: Fetches live journey information from Transport NSW API
- **E-Paper Optimized**: Designed specifically for e-paper displays with high contrast
- **Hardware Support**: Works with actual e-paper displays (Waveshare, etc.)
- **Partial Updates**: Updates only time display without full screen refresh
- **Simulation Mode**: Test without hardware using Tkinter or file output
- **Modular Design**: Clean separation of concerns with dedicated modules
- **Live Updates**: Automatic refresh of journey data
- **Production Ready**: Continuous mode for 24/7 operation

## File Structure

```
transport_display/
├── main.py                    # Main entry point
├── models.py                  # Data models and configuration classes
├── font_manager.py            # Font loading and caching functionality
├── journey_data_service.py    # API data fetching and processing
├── display_renderer.py        # Image rendering and drawing logic
├── hardware_display_manager.py # Hardware display integration
├── partial_updater.py         # Partial update system for time display
├── display_manager.py         # Legacy mock display (for reference)
├── journey_display.py         # Main journey display controller
├── utils.py                   # Utility functions
├── README.md                  # This file
└── legacy/                    # Original monolithic file (for reference)
    └── mock_text_updater_sim.py
```

## Module Descriptions

### `models.py`

Contains all data models and configuration classes:

- `TransportMode` - Enum for transport types
- `JourneyStop` - Data model for journey stops with properties for display formatting
- `DisplayConfig` - Configuration for display settings (dimensions, fonts, etc.)
- `JourneyConfig` - Configuration for journey settings (stop IDs, update intervals)

### `font_manager.py`

Handles font loading and caching:

- `FontManager` - Manages font loading with caching for performance
- Supports Arial and Arial Bold fonts with fallback to default

### `journey_data_service.py`

Handles API communication and data processing:

- `JourneyDataService` - Fetches and processes journey data from Transport NSW API
- Converts raw API data to `JourneyStop` objects
- Handles data validation and filtering

### `display_renderer.py`

Handles all image rendering:

- `DisplayRenderer` - Creates journey display images
- Renders banner, info box, stops list, and time display
- Uses PIL for image creation and drawing

### `hardware_display_manager.py`

Manages hardware e-paper display integration:

- `HardwareDisplayManager` - Integrates with the existing display infrastructure
- Supports both hardware and simulation modes
- Uses the display factory pattern for flexibility
- **Partial Updates**: Implements `display_Partial` for efficient time updates

### `partial_updater.py`

Handles partial display updates:

- `PartialUpdater` - Creates partial update images for time display
- Calculates regions for banner time and next service time
- Optimizes e-paper refresh by updating only changing areas

### `journey_display.py`

Main controller class:

- `JourneyDisplay` - Orchestrates the entire display system
- Manages the demo loop and display updates
- Coordinates between data service, renderer, and display
- **Smart Updates**: Uses full updates for journey changes, partial updates for time

### `utils.py`

Utility functions:

- `get_api_key()` - Retrieves API key from environment or user input

## Usage

### Running the Transport Display

#### Hardware Mode (Default)

```bash
# Basic hardware mode (uses default e-paper module)
python main.py

# Specify a particular e-paper module
python main.py --epd-module epd7in5b_V2

# Continuous mode (production use)
python main.py

# Demo mode with custom duration
python main.py --demo --duration 600

# Test partial updates only
python main.py --test-partial
```

#### Simulation Mode

```bash
# Simulation mode with live display
python main.py --simulate

# Simulation demo mode
python main.py --simulate --demo --duration 300

# Test partial updates in simulation
python main.py --simulate --test-partial
```

#### Debug Mode

```bash
# Enable debug logging
python main.py --debug

# Simulation with debug
python main.py --simulate --debug
```

### Command Line Options

- `--simulate`: Run in simulation mode (default: hardware mode)
- `--demo`: Run in demo mode with limited duration (default: continuous mode)
- `--duration SECONDS`: Duration for demo mode (default: 300)
- `--debug`: Enable debug logging
- `--epd-module MODULE`: Specify e-paper module to use
- `--test-partial`: Test partial updates only (for development)

### API Key Setup

You'll need a Transport NSW API key. You can either:

1. Set the environment variable:

   ```bash
   export TRANSPORT_API_KEY="your-api-key-here"
   ```

2. Or enter it when prompted by the application

## Hardware Setup

### Supported E-Paper Displays

The system works with any e-paper display that has a Waveshare-compatible driver. Common models include:

- 7.5" e-paper displays (epd7in5b_V2)
- 5.83" e-paper displays
- 2.13" e-paper displays

### Installation

1. Install the Waveshare e-paper library:

   ```bash
   pip install waveshare-epaper
   ```

2. Connect your e-paper display to your Raspberry Pi or other compatible device

3. Run the transport display:
   ```bash
   python main.py
   ```

### Running from Project Root

To run from the project root directory:

```bash
cd /path/to/e-paper-main
python3 -m apps.transport_display.main
```

## Configuration

### Journey Settings

- **Origin**: Rhodes Station (ID: 213891)
- **Destination**: Central Station (ID: 10101100)
- **Update Interval**: 60 seconds (configurable)
- **Max Stops**: 10 stops displayed

### Display Settings

- **Resolution**: 800x480 pixels
- **Banner Height**: 60 pixels
- **Info Box Height**: 80 pixels
- **Content Padding**: 20 pixels

### Update Intervals

- **Full Updates**: Every 60 seconds (when journey data changes)
- **Partial Updates**: Every 60 seconds (for time display only)

## Dependencies

- `PIL` (Pillow) for image processing
- `tkinter` for simulation display (optional)
- `waveshare-epaper` for hardware support
- Custom `transport_api` module from the `lib` directory

## Production Deployment

For 24/7 operation:

1. Set up as a system service
2. Use continuous mode (default)
3. Configure automatic restart on failure
4. Monitor API rate limits

Example systemd service:

```ini
[Unit]
Description=Transport Display System
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/path/to/e-paper-main/apps/transport_display
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10
Environment=TRANSPORT_API_KEY=your-api-key

[Install]
WantedBy=multi-user.target
```

## Benefits of Modular Structure

1. **Maintainability** - Each module has a single responsibility
2. **Testability** - Individual components can be tested in isolation
3. **Reusability** - Components can be reused in other projects
4. **Readability** - Smaller files are easier to understand
5. **Collaboration** - Multiple developers can work on different modules
6. **Debugging** - Easier to locate and fix issues in specific modules
7. **Hardware Integration** - Clean separation between display logic and hardware interface
8. **Partial Updates** - Optimized e-paper refresh system

## Troubleshooting

### Common Issues

1. **Import Error for e-paper module**

   - Install waveshare-epaper: `pip install waveshare-epaper`
   - Or use simulation mode: `python main.py --simulate`

2. **API Key not found**

   - Set environment variable: `export TRANSPORT_API_KEY="your-key"`
   - Or enter when prompted

3. **Display not updating**

   - Check hardware connections
   - Verify e-paper module compatibility
   - Use simulation mode to test: `python main.py --simulate`

4. **Permission errors**

   - Run with sudo if needed for hardware access
   - Check SPI permissions on Raspberry Pi

5. **Partial updates not working**
   - Ensure e-paper module supports `display_Partial`
   - Check that `init_part()` is called during initialization
   - Use `--test-partial` flag to debug partial updates
