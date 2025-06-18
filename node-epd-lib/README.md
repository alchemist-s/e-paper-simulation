# Node.js E-Paper Display Library

A Node.js library for controlling e-paper displays, specifically designed for the 7.5" Waveshare e-paper display (epd7in5b_V2).

## Features

- **Hardware Support**: Direct control of e-paper displays via SPI and GPIO
- **Async/Await**: Modern JavaScript with full async support
- **7.5" Display Support**: Optimized for the epd7in5b_V2 display
- **Clean API**: Simple and intuitive interface
- **Error Handling**: Comprehensive error handling and cleanup
- **Image Processing**: Full image conversion and rotation support
- **Partial Updates**: Support for partial display updates
- **Multiple Init Modes**: Standard, Fast, and Partial initialization modes
- **Multiple GPIO Libraries**: Support for pigpio, onoff, rpi-gpio, and file system GPIO

## Installation

### Prerequisites

1. **Node.js**: Version 14 or higher
2. **Raspberry Pi**: Tested on Raspberry Pi 4
3. **Hardware**: 7.5" Waveshare e-paper display

### Install Dependencies

```bash
# Navigate to the node-epd-lib directory
cd node-epd-lib

# Install dependencies
npm install
```

### Hardware Setup

1. **Connect the e-paper display** to your Raspberry Pi:

   - VCC → 3.3V
   - GND → GND
   - DIN → GPIO10 (MOSI)
   - CLK → GPIO11 (SCLK)
   - CS → GPIO8
   - DC → GPIO25
   - RST → GPIO17
   - BUSY → GPIO24
   - PWR → GPIO18

2. **Enable SPI** on your Raspberry Pi:

   ```bash
   sudo raspi-config
   # Navigate to: Interface Options → SPI → Enable
   ```

3. **Install system dependencies**:
   ```bash
   sudo apt-get update
   sudo apt-get install build-essential python3-dev
   ```

## GPIO Configuration Options

The library supports multiple GPIO libraries for different use cases:

### 1. pigpio (Recommended for Raspberry Pi)

**Best for**: High-performance applications requiring precise timing and microsecond accuracy.

**Features**:

- Fast GPIO operations with microsecond precision
- Interrupt handling and state change notifications
- PWM and servo control capabilities
- Hardware-level timing accuracy
- BCM GPIO numbering (compatible with gpiozero)

**Installation**:

```bash
# Install pigpio C library
sudo apt-get install pigpio

# Install Node.js pigpio package
npm install pigpio
```

**Usage**:

```bash
# Run with sudo (required for pigpio)
sudo node examples/minimal-test-pigpio.js
```

**Documentation**: See [README-PIGPIO.md](README-PIGPIO.md) for detailed pigpio configuration and usage.

### 2. onoff (Alternative)

**Best for**: Simple GPIO operations without root privileges.

**Features**:

- No root privileges required
- Simple API
- Interrupt support
- BCM GPIO numbering

**Installation**:

```bash
npm install onoff
```

### 3. rpi-gpio (Legacy)

**Best for**: Legacy applications or compatibility with older code.

**Features**:

- Traditional GPIO library
- No root privileges required
- BCM GPIO numbering

**Installation**:

```bash
npm install rpi-gpio
```

### 4. File System GPIO (Fallback)

**Best for**: Systems where native GPIO libraries fail to build.

**Features**:

- Direct file system access to GPIO
- No native dependencies
- Works on all Linux systems
- Requires correct GPIO chip numbering

**Usage**:

```bash
# May require different GPIO numbers on some Pi models
node examples/minimal-test-fs.js
```

## Quick Start

### Basic Usage

```javascript
const { EPD7in5bV2 } = require("./index");

async function main() {
  const epd = new EPD7in5bV2();

  try {
    // Initialize the display
    await epd.init();

    // Clear the display
    await epd.clear();

    // Create and display a bordered box
    const blackBuffer = epd.createBorderedBox();
    const redBuffer = Buffer.alloc(
      Math.floor(epd.WIDTH / 8) * epd.HEIGHT,
      0x00
    );

    await epd.display(blackBuffer, redBuffer);

    // Put display to sleep
    await epd.sleep();
  } catch (error) {
    console.error("Error:", error);
  }
}

main();
```

### Run the Example

```bash
# Run the bordered box example
npm start

# Or run directly
node examples/bordered-box.js
```

## API Reference

### EPD7in5bV2 Class

#### Constructor

```javascript
const epd = new EPD7in5bV2();
```

#### Methods

##### `async init()`

Initialize the e-paper display hardware (standard mode).

- **Returns**: `0` on success, `-1` on failure

##### `async init_Fast()`

Initialize the e-paper display hardware (fast mode).

- **Returns**: `0` on success, `-1` on failure

##### `async init_part()`

Initialize the e-paper display hardware (partial update mode).

- **Returns**: `0` on success, `-1` on failure

##### `async clear()`

Clear the display to white.

##### `async display(imageBlack, imageRed)`

Display images on the screen.

- **Parameters**:
  - `imageBlack`: Buffer containing black/white image data
  - `imageRed`: Buffer containing red image data

##### `async display_Base_color(color)`

Display a solid color on the screen.

- **Parameters**:
  - `color`: Byte value for the color

##### `async display_Partial(image, xStart, yStart, xEnd, yEnd)`

Update a specific region of the display.

- **Parameters**:
  - `image`: Buffer containing image data
  - `xStart, yStart`: Starting coordinates
  - `xEnd, yEnd`: Ending coordinates

##### `async sleep()`

Put the display to sleep and cleanup hardware.

##### `getBuffer(image)`

Convert a canvas/image to the proper buffer format for the display.

- **Parameters**:
  - `image`: Canvas object or image with getImageData method
- **Returns**: Buffer containing the converted image data

##### `createBorderedBox()`

Create a simple bordered box image.

- **Returns**: Buffer containing the image data

### EPDConfig Class

#### Methods

##### `async init()`

Initialize the hardware configuration.

##### `async digitalWrite(pin, value)`

Write a digital value to a GPIO pin.

##### `async digitalRead(pin)`

Read a digital value from a GPIO pin.

##### `async spiWrite(data)`

Write data via SPI.

##### `async delay(ms)`

Delay execution for specified milliseconds.

##### `async moduleExit()`

Cleanup hardware resources.

## Examples

### Display a Simple Border

```javascript
const { EPD7in5bV2 } = require("./index");

async function showBorder() {
  const epd = new EPD7in5bV2();

  try {
    await epd.init();
    await epd.clear();

    const blackBuffer = epd.createBorderedBox();
    const redBuffer = Buffer.alloc(
      Math.floor(epd.WIDTH / 8) * epd.HEIGHT,
      0x00
    );

    await epd.display(blackBuffer, redBuffer);
    await epd.sleep();
  } catch (error) {
    console.error("Error:", error);
  }
}

showBorder();
```

### Custom Image Display

```javascript
const { createCanvas } = require("canvas");
const { EPD7in5bV2 } = require("./index");

async function displayCustomImage() {
  const epd = new EPD7in5bV2();

  try {
    await epd.init();

    // Create a custom image
    const canvas = createCanvas(epd.WIDTH, epd.HEIGHT);
    const ctx = canvas.getContext("2d");

    // Draw something
    ctx.fillStyle = "white";
    ctx.fillRect(0, 0, epd.WIDTH, epd.HEIGHT);

    ctx.fillStyle = "black";
    ctx.font = "48px Arial";
    ctx.fillText("Hello E-Paper!", 100, 240);

    // Convert to buffer using the getBuffer method
    const blackBuffer = epd.getBuffer(canvas);
    const redBuffer = Buffer.alloc(
      Math.floor(epd.WIDTH / 8) * epd.HEIGHT,
      0x00
    );

    await epd.display(blackBuffer, redBuffer);
    await epd.sleep();
  } catch (error) {
    console.error("Error:", error);
  }
}

displayCustomImage();
```

### Partial Update Example

```javascript
const { EPD7in5bV2 } = require("./index");

async function partialUpdateExample() {
  const epd = new EPD7in5bV2();

  try {
    // Initialize for partial updates
    await epd.init_part();

    // Create a small image for partial update
    const partialImage = Buffer.alloc(1000); // Small buffer for demo

    // Update a specific region (e.g., top-left corner)
    await epd.display_Partial(partialImage, 0, 0, 100, 100);

    await epd.sleep();
  } catch (error) {
    console.error("Error:", error);
  }
}

partialUpdateExample();
```

## Image Processing

The library includes comprehensive image processing capabilities:

### Image Conversion

- **Automatic 1-bit conversion**: Converts any image to black/white
- **Rotation support**: Handles images that need to be rotated
- **Size validation**: Ensures images match display dimensions
- **Buffer optimization**: Efficient memory usage

### Supported Image Formats

- Canvas objects (from node-canvas)
- Any object with `getImageData()` method
- Automatic handling of RGBA to 1-bit conversion

### Buffer Format

- **Resolution**: 800x480 pixels
- **Color depth**: 1-bit (black/white)
- **Buffer size**: 48,000 bytes (800/8 \* 480)
- **Bit packing**: 8 pixels per byte

## Testing

### Test Buffer Conversion Logic

```bash
# Test the buffer conversion without hardware
node examples/test-buffer-only.js
```

### Test Hardware (on Raspberry Pi)

```bash
# Test hardware connectivity
node test.js
```

## Troubleshooting

### Common Issues

1. **Permission Denied**

   ```bash
   # Add user to gpio and spi groups
   sudo usermod -a -G gpio,spi $USER
   # Logout and login again
   ```

2. **SPI Not Available**

   ```bash
   # Check if SPI is enabled
   ls /dev/spidev*
   # Should show: /dev/spidev0.0
   ```

3. **GPIO Access Issues**

   ```bash
   # Check GPIO permissions
   ls -la /sys/class/gpio/
   ```

4. **Native Module Build Failures**

   ```bash
   # Install build tools
   sudo apt-get install build-essential python3-dev
   # Rebuild modules
   npm rebuild
   ```

5. **Canvas Library Issues (macOS)**
   ```bash
   # Canvas may not work on macOS, but buffer logic can be tested
   node examples/test-buffer-only.js
   ```

### Debug Mode

Enable debug logging by setting the environment variable:

```bash
DEBUG=* node examples/bordered-box.js
```

## Development

### Project Structure

```
node-epd-lib/
├── src/
│   ├── epd-config.js      # Hardware configuration
│   └── epd7in5b-v2.js     # Display driver
├── examples/
│   ├── bordered-box.js    # Example application
│   ├── test-getbuffer.js  # Buffer testing (requires canvas)
│   ├── test-getbuffer-simple.js  # Buffer testing (no canvas)
│   └── test-buffer-only.js # Standalone buffer logic test
├── package.json
├── index.js
├── test.js
└── README.md
```

### Adding New Features

1. **New Display Types**: Extend the base classes in `src/`
2. **New Examples**: Add to the `examples/` directory
3. **Testing**: Add test cases to `test.js`

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions:

1. Check the troubleshooting section
2. Search existing issues
3. Create a new issue with detailed information
