# E-Paper Display Library - pigpio Configuration

This document provides detailed information about using the e-paper display library with the **pigpio** library on Raspberry Pi.

## Overview

The pigpio configuration provides fast GPIO operations with microsecond precision, making it ideal for e-paper displays that require precise timing. pigpio is a high-performance GPIO library that offers:

- **Fast GPIO operations** with microsecond precision
- **Interrupt handling** and state change notifications
- **PWM and servo control** capabilities
- **Hardware-level timing accuracy**
- **BCM GPIO numbering** (compatible with gpiozero)

## Requirements

### Hardware

- Raspberry Pi (Zero, 1, 2, 3, or 4)
- 7.5" Waveshare e-paper display
- Proper wiring connections

### Software

- Node.js 10, 12, 14, 15, or 16
- pigpio C library
- Root/sudo privileges

## Installation

### 1. Install pigpio C Library

```bash
sudo apt-get update
sudo apt-get install pigpio
```

### 2. Install Node.js Dependencies

```bash
npm install pigpio spi-device
```

### 3. Enable SPI (if not already enabled)

```bash
sudo raspi-config
# Navigate to: Interface Options > SPI > Enable
```

## GPIO Pin Configuration

The library uses BCM GPIO numbering (same as gpiozero):

| Pin  | GPIO | Function     | Direction |
| ---- | ---- | ------------ | --------- |
| RST  | 17   | Reset        | Output    |
| DC   | 25   | Data/Command | Output    |
| CS   | 8    | Chip Select  | Output    |
| BUSY | 24   | Busy         | Input     |
| PWR  | 18   | Power        | Output    |

### Wiring Diagram

```
Raspberry Pi 4    E-Paper Display
-------------    ----------------
GPIO 17 (RST) -> RST
GPIO 25 (DC)  -> DC
GPIO 8  (CS)  -> CS
GPIO 24 (BUSY)-> BUSY
GPIO 18 (PWR) -> PWR
3.3V          -> VCC
GND           -> GND
```

## Usage

### Basic Example

```javascript
const EPDConfigPigpio = require("./src/epd-config-pigpio");

async function main() {
  const epdConfig = new EPDConfigPigpio();

  try {
    // Initialize hardware
    await epdConfig.init();

    // Your e-paper operations here
    await epdConfig.digitalWrite(epdConfig.RST_PIN, 1);
    await epdConfig.delay(100);

    // Cleanup
    await epdConfig.moduleExit();
  } catch (error) {
    console.error("Error:", error);
  }
}

main();
```

### Running with Sudo

**Important**: pigpio requires root privileges to access hardware:

```bash
sudo node your-script.js
```

## API Reference

### EPDConfigPigpio Class

#### Constructor

```javascript
const epdConfig = new EPDConfigPigpio();
```

#### Methods

##### `async init()`

Initializes the e-paper display hardware.

- Sets up GPIO pins
- Configures SPI communication
- Powers on the display

**Returns**: `Promise<number>` - 0 on success

##### `async digitalWrite(pin, value)`

Writes a digital value to a GPIO pin.

**Parameters**:

- `pin` (number): GPIO pin number (BCM)
- `value` (number|boolean): Value to write (1/true for high, 0/false for low)

##### `async digitalRead(pin)`

Reads a digital value from a GPIO pin.

**Parameters**:

- `pin` (number): GPIO pin number (BCM)

**Returns**: `Promise<number>` - Pin value (0 or 1)

##### `async spiWrite(data)`

Writes data over SPI.

**Parameters**:

- `data` (Array<number>|Buffer): Data to write

**Returns**: `Promise<Buffer>` - Received data

##### `async delay(ms)`

Waits for a specified number of milliseconds.

**Parameters**:

- `ms` (number): Milliseconds to wait

##### `async delayMicroseconds(us)`

Waits for a specified number of microseconds with high precision.

**Parameters**:

- `us` (number): Microseconds to wait

##### `async waitForReady(timeout)`

Waits for the busy pin to go low (display ready).

**Parameters**:

- `timeout` (number): Timeout in milliseconds (default: 5000ms)

**Returns**: `Promise<boolean>` - True if ready, false if timeout

##### `async moduleExit()`

Cleans up hardware resources.

##### `getPinInfo()`

Returns pin configuration information.

**Returns**: `Object` - Pin configuration details

## Testing

### Run Minimal Hardware Test

```bash
sudo node examples/minimal-test-pigpio.js
```

This test verifies:

- Hardware initialization
- GPIO read/write operations
- SPI communication
- Microsecond delay precision
- Display reset sequence
- Basic display commands
- Resource cleanup

### Expected Output

```
Minimal E-Paper Hardware Test (pigpio)
=====================================
Using pigpio library for fast GPIO operations

1. Testing hardware initialization...
✅ Hardware initialized successfully

2. Testing GPIO operations...
✅ GPIO write operations successful

3. Testing GPIO read operations...
   BUSY pin value: 1
✅ GPIO read operations successful

4. Testing SPI operations...
   Sent: [0, 1, 2, 3]
   Received: [0, 0, 0, 0]
✅ SPI write operations successful

5. Testing microsecond delay precision...
   Requested: 1ms, Actual: 1.002ms
✅ Microsecond delay precision test successful

...

🎉 All hardware tests passed!
```

## Troubleshooting

### Common Issues

#### 1. Permission Denied

```
Error: EACCES: permission denied
```

**Solution**: Run with sudo privileges

```bash
sudo node your-script.js
```

#### 2. pigpio Not Found

```
Error: Cannot find module 'pigpio'
```

**Solution**: Install pigpio C library and Node.js package

```bash
sudo apt-get install pigpio
npm install pigpio
```

#### 3. GPIO Pin Already in Use

```
Error: GPIO pin already in use
```

**Solution**: Check for conflicting processes

```bash
sudo pkill -f pigpiod
sudo node your-script.js
```

#### 4. SPI Not Enabled

```
Error: SPI device not found
```

**Solution**: Enable SPI in raspi-config

```bash
sudo raspi-config
# Interface Options > SPI > Enable
```

#### 5. Incorrect Pin Numbers

```
Error: Invalid GPIO pin
```

**Solution**: Verify BCM pin numbers and wiring

### Performance Tips

1. **Use microsecond delays** for precise timing:

   ```javascript
   await epdConfig.delayMicroseconds(1000); // 1ms with microsecond precision
   ```

2. **Monitor busy pin** for display readiness:

   ```javascript
   const ready = await epdConfig.waitForReady(5000);
   if (!ready) {
     console.log("Display timeout");
   }
   ```

3. **Lower SPI speed** for reliability:
   ```javascript
   this.SPI_MAX_SPEED = 1000000; // 1MHz
   ```

## Comparison with Other GPIO Libraries

| Feature       | pigpio     | onoff  | rpi-gpio | File System |
| ------------- | ---------- | ------ | -------- | ----------- |
| Speed         | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐     | ⭐⭐        |
| Precision     | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐     | ⭐⭐        |
| BCM Support   | ✅         | ✅     | ✅       | ❌          |
| Interrupts    | ✅         | ✅     | ❌       | ❌          |
| PWM           | ✅         | ❌     | ❌       | ❌          |
| Root Required | ✅         | ❌     | ❌       | ❌          |

## Advanced Features

### Interrupt Handling

pigpio supports interrupt handling for GPIO state changes:

```javascript
const Gpio = require("pigpio").Gpio;

const button = new Gpio(23, {
  mode: Gpio.INPUT,
  pullUpDown: Gpio.PUD_UP,
  alert: true,
});

button.on("alert", (level, tick) => {
  console.log(`Button pressed at tick ${tick}`);
});
```

### PWM Control

pigpio provides hardware PWM capabilities:

```javascript
const led = new Gpio(17, { mode: Gpio.OUTPUT });
led.pwmWrite(128); // 50% duty cycle
```

### Waveform Generation

For complex timing patterns:

```javascript
const pigpio = require("pigpio");
pigpio.waveClear();
pigpio.waveAddGeneric([
  { gpioOn: 17, gpioOff: 0, usDelay: 1000 },
  { gpioOn: 0, gpioOff: 17, usDelay: 1000 },
]);
const waveId = pigpio.waveCreate();
pigpio.waveTxSend(waveId, pigpio.WAVE_MODE_ONE_SHOT);
```

## Resources

- [pigpio GitHub Repository](https://github.com/fivdi/pigpio)
- [pigpio C Library Documentation](http://abyz.me.uk/rpi/pigpio/)
- [Raspberry Pi GPIO Documentation](https://www.raspberrypi.org/documentation/usage/gpio/)
- [SPI Interface Guide](https://www.raspberrypi.org/documentation/hardware/raspberrypi/spi/)

## License

This library is licensed under the MIT License. See the main README for details.
