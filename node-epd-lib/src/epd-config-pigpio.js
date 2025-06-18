/**
 * E-Paper Display Configuration using pigpio
 *
 * This module provides hardware abstraction for controlling e-paper displays
 * using the pigpio library on Raspberry Pi. pigpio is a fast GPIO library
 * that provides precise timing and interrupt handling capabilities.
 *
 * Features:
 * - Fast GPIO operations with microsecond precision
 * - Interrupt handling and state change notifications
 * - PWM and servo control capabilities
 * - Hardware-level timing accuracy
 *
 * Requirements:
 * - Raspberry Pi (Zero, 1, 2, 3, or 4)
 * - Node.js 10, 12, 14, 15, or 16
 * - Root/sudo privileges (pigpio requires hardware access)
 * - pigpio C library installed: sudo apt-get install pigpio
 *
 * Installation:
 * 1. Install pigpio C library: sudo apt-get install pigpio
 * 2. Install Node.js pigpio: npm install pigpio
 * 3. Run with sudo: sudo node your-script.js
 *
 * GPIO Pin Configuration (BCM numbering):
 * - RST_PIN: GPIO 17 - Reset pin
 * - DC_PIN:  GPIO 25 - Data/Command pin
 * - CS_PIN:  GPIO 8  - Chip Select pin
 * - BUSY_PIN: GPIO 24 - Busy pin (input)
 * - PWR_PIN: GPIO 18 - Power control pin
 *
 * @see https://github.com/fivdi/pigpio
 */

const SpiDevice = require("spi-device");
const Gpio = require("pigpio").Gpio;

class EPDConfigPigpio {
  constructor() {
    // Pin definitions for 7.5" e-paper display (BCM numbering like gpiozero)
    this.RST_PIN = 17;
    this.DC_PIN = 25;
    this.CS_PIN = 8;
    this.BUSY_PIN = 24;
    this.PWR_PIN = 18;

    // SPI configuration
    this.SPI_BUS = 0;
    this.SPI_DEVICE = 0;
    this.SPI_MODE = 0;
    this.SPI_MAX_SPEED = 1000000; // 1MHz for reliability

    // GPIO and SPI objects
    this.gpioPins = {};
    this.spi = null;

    this.initialized = false;
  }

  /**
   * Initialize the e-paper display hardware
   *
   * This method sets up GPIO pins and SPI communication for the e-paper display.
   * It must be called before any other operations.
   *
   * @returns {Promise<number>} 0 on success
   * @throws {Error} If initialization fails
   */
  async init() {
    try {
      console.log("Initializing e-paper hardware (pigpio)...");

      // Set up GPIO pins
      await this.setupGPIO();

      // Power on the display
      await this.digitalWrite(this.PWR_PIN, 1);

      // Initialize SPI
      this.spi = SpiDevice.openSync(this.SPI_BUS, this.SPI_DEVICE);
      this.spi.setOptionsSync({
        mode: this.SPI_MODE,
        maxSpeedHz: this.SPI_MAX_SPEED,
      });

      this.initialized = true;
      console.log("E-paper hardware initialized successfully");
      return 0;
    } catch (error) {
      console.error("Failed to initialize e-paper hardware:", error);
      throw error;
    }
  }

  /**
   * Set up GPIO pins for e-paper display control
   *
   * Configures all GPIO pins with appropriate modes:
   * - Output pins: RST, DC, CS, PWR
   * - Input pin: BUSY
   *
   * @throws {Error} If GPIO setup fails
   */
  async setupGPIO() {
    try {
      // Set up output pins
      const outputPins = [this.RST_PIN, this.DC_PIN, this.CS_PIN, this.PWR_PIN];

      for (const pin of outputPins) {
        this.gpioPins[pin] = new Gpio(pin, {
          mode: Gpio.OUTPUT,
          pullUpDown: Gpio.PUD_OFF, // No pull-up/down resistors
        });
        console.log(`Set GPIO ${pin} to output`);
      }

      // Set up input pin with pull-up resistor for reliable reading
      this.gpioPins[this.BUSY_PIN] = new Gpio(this.BUSY_PIN, {
        mode: Gpio.INPUT,
        pullUpDown: Gpio.PUD_UP, // Pull-up resistor for stable reading
        alert: false, // No alerts for busy pin
      });
      console.log(`Set GPIO ${this.BUSY_PIN} to input with pull-up`);

      console.log("GPIO pins set up successfully");
    } catch (error) {
      console.error("Failed to setup GPIO:", error);
      throw error;
    }
  }

  /**
   * Write a digital value to a GPIO pin
   *
   * @param {number} pin - GPIO pin number (BCM)
   * @param {number|boolean} value - Value to write (1/true for high, 0/false for low)
   * @throws {Error} If EPD not initialized or write fails
   */
  async digitalWrite(pin, value) {
    if (!this.initialized) {
      throw new Error("EPD not initialized. Call init() first.");
    }

    try {
      this.gpioPins[pin].digitalWrite(value ? 1 : 0);
    } catch (error) {
      console.error(`Failed to write to pin ${pin}:`, error);
      throw error;
    }
  }

  /**
   * Read a digital value from a GPIO pin
   *
   * @param {number} pin - GPIO pin number (BCM)
   * @returns {Promise<number>} Pin value (0 or 1)
   * @throws {Error} If EPD not initialized or read fails
   */
  async digitalRead(pin) {
    if (!this.initialized) {
      throw new Error("EPD not initialized. Call init() first.");
    }

    try {
      return this.gpioPins[pin].digitalRead();
    } catch (error) {
      console.error(`Failed to read from pin ${pin}:`, error);
      throw error;
    }
  }

  /**
   * Write data over SPI
   *
   * @param {Array<number>|Buffer} data - Data to write
   * @returns {Promise<Buffer>} Received data
   * @throws {Error} If EPD not initialized or SPI write fails
   */
  async spiWrite(data) {
    if (!this.initialized) {
      throw new Error("EPD not initialized. Call init() first.");
    }

    try {
      return new Promise((resolve, reject) => {
        this.spi.transfer(
          [
            {
              byteLength: data.length,
              sendBuffer: Buffer.from(data),
              receiveBuffer: Buffer.alloc(data.length),
            },
          ],
          (err, message) => {
            if (err) {
              reject(err);
            } else {
              resolve(message[0].receiveBuffer);
            }
          }
        );
      });
    } catch (error) {
      console.error("SPI write failed:", error);
      throw error;
    }
  }

  /**
   * Wait for a specified number of milliseconds
   *
   * @param {number} ms - Milliseconds to wait
   * @returns {Promise<void>}
   */
  async delay(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  /**
   * Wait for a specified number of microseconds
   *
   * @param {number} us - Microseconds to wait
   * @returns {Promise<void>}
   */
  async delayMicroseconds(us) {
    return new Promise((resolve) => {
      const start = process.hrtime.bigint();
      while (process.hrtime.bigint() - start < BigInt(us * 1000)) {
        // Busy wait for microsecond precision
      }
      resolve();
    });
  }

  /**
   * Wait for the busy pin to go low (display ready)
   *
   * @param {number} timeout - Timeout in milliseconds (default: 5000ms)
   * @returns {Promise<boolean>} True if ready, false if timeout
   */
  async waitForReady(timeout = 5000) {
    const startTime = Date.now();

    while (Date.now() - startTime < timeout) {
      const busy = await this.digitalRead(this.BUSY_PIN);
      if (busy === 0) {
        return true; // Display is ready
      }
      await this.delay(10); // Check every 10ms
    }

    return false; // Timeout
  }

  /**
   * Clean up hardware resources
   *
   * This method should be called when the application is shutting down
   * to properly release GPIO pins and SPI resources.
   */
  async moduleExit() {
    if (!this.initialized) {
      return;
    }

    try {
      console.log("Cleaning up e-paper hardware...");

      // Close SPI
      if (this.spi) {
        this.spi.closeSync();
      }

      // Power off GPIO
      await this.digitalWrite(this.RST_PIN, 0);
      await this.digitalWrite(this.DC_PIN, 0);
      await this.digitalWrite(this.PWR_PIN, 0);

      // Close GPIO pins
      for (const pin of Object.values(this.gpioPins)) {
        if (pin) {
          pin.unexport();
        }
      }

      this.initialized = false;
      console.log("E-paper hardware cleanup completed");
    } catch (error) {
      console.error("Error during cleanup:", error);
    }
  }

  /**
   * Get GPIO pin information
   *
   * @returns {Object} Pin configuration information
   */
  getPinInfo() {
    return {
      RST_PIN: this.RST_PIN,
      DC_PIN: this.DC_PIN,
      CS_PIN: this.CS_PIN,
      BUSY_PIN: this.BUSY_PIN,
      PWR_PIN: this.PWR_PIN,
      SPI_BUS: this.SPI_BUS,
      SPI_DEVICE: this.SPI_DEVICE,
      SPI_MODE: this.SPI_MODE,
      SPI_MAX_SPEED: this.SPI_MAX_SPEED,
    };
  }
}

module.exports = EPDConfigPigpio;
