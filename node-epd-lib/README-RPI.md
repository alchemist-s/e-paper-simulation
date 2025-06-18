# Node.js E-Paper Library for Raspberry Pi

This library provides Node.js bindings for controlling Waveshare e-paper displays on Raspberry Pi.

## Hardware Requirements

- Raspberry Pi (any model with GPIO pins)
- Waveshare 7.5" e-paper display (EPD7in5b_V2)
- Proper wiring connections

## Pin Connections

Connect your e-paper display to the Raspberry Pi using these GPIO pins (BCM numbering):

| E-Paper Pin | Raspberry Pi GPIO | Function      |
| ----------- | ----------------- | ------------- |
| RST         | GPIO 17           | Reset         |
| DC          | GPIO 25           | Data/Command  |
| CS          | GPIO 8            | Chip Select   |
| BUSY        | GPIO 24           | Busy Signal   |
| PWR         | GPIO 18           | Power Control |
| MOSI        | GPIO 10           | SPI MOSI      |
| SCLK        | GPIO 11           | SPI SCLK      |
| GND         | GND               | Ground        |
| VCC         | 3.3V              | Power         |

## Installation on Raspberry Pi

1. **Install Node.js** (if not already installed):

   ```bash
   curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
   sudo apt-get install -y nodejs
   ```

2. **Enable SPI and GPIO**:

   ```bash
   sudo raspi-config
   # Navigate to: Interface Options > SPI > Enable
   # Navigate to: Interface Options > GPIO > Enable
   ```

3. **Add user to required groups**:

   ```bash
   sudo usermod -a -G spi,gpio $USER
   # Log out and back in for changes to take effect
   ```

4. **Clone and install the library**:
   ```bash
   git clone <repository-url>
   cd node-epd-lib
   npm install
   ```

## Usage

### Basic Hardware Test

Test if your hardware is working correctly:

```bash
npm run start-rpi
```

This will:

- Initialize GPIO pins using the `rpi-gpio` library
- Test SPI communication
- Test basic display commands
- Clean up resources

### Display a Bordered Box

Show a simple bordered box on the display:

```bash
# Using the rpi-gpio version (recommended)
node examples/bordered-box-rpi-gpio.js
```

### Programmatic Usage

```javascript
const EPDConfigRPiGPIO = require("./src/epd-config-rpi-gpio");
const EPD7in5bV2RPiGPIO = require("./src/epd7in5b-v2-rpi-gpio");

async function main() {
  const epd = new EPD7in5bV2RPiGPIO();

  // Initialize the display
  await epd.init();

  // Create and display an image
  const blackBuffer = epd.createBorderedBox();
  const redBuffer = epd.createEmptyBuffer();

  await epd.display(blackBuffer, redBuffer);

  // Clean up
  await epd.sleep();
}

main().catch(console.error);
```

## Troubleshooting

### Permission Errors

If you get permission errors:

```bash
# Check if you're in the right groups
groups

# If not in spi or gpio groups, add yourself:
sudo usermod -a -G spi,gpio $USER
# Then log out and back in
```

### GPIO Errors

If GPIO pins are already in use:

```bash
# Check what's using GPIO
ls /sys/class/gpio/

# Clean up any existing exports
echo 17 > /sys/class/gpio/unexport
echo 25 > /sys/class/gpio/unexport
echo 8 > /sys/class/gpio/unexport
echo 24 > /sys/class/gpio/unexport
echo 18 > /sys/class/gpio/unexport
```

### SPI Errors

If SPI is not working:

```bash
# Check if SPI is enabled
ls /dev/spidev*

# Should show: /dev/spidev0.0

# If not, enable SPI in raspi-config
sudo raspi-config
```

## Why This Version Works

The `rpi-gpio` library:

- Uses the correct BCM GPIO numbering for Raspberry Pi
- Handles GPIO initialization properly
- Provides proper async/await support
- Manages GPIO state correctly

This is equivalent to how the Python version uses `gpiozero` - it abstracts the hardware-specific details and provides a clean API.

## Alternative Approaches

If `rpi-gpio` doesn't work, you can try:

1. **File system GPIO** (less reliable):

   ```bash
   npm run start-fs
   ```

2. **Native modules** (may have build issues):
   ```bash
   npm install onoff
   ```

The `rpi-gpio` approach is recommended as it's the most reliable and matches the Python implementation's approach.
