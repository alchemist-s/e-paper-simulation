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
    this.SPI_MAX_SPEED = 1000000; // 1MHz

    // GPIO and SPI objects
    this.gpioPins = {};
    this.spi = null;

    this.initialized = false;
  }

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

  async setupGPIO() {
    try {
      // Set up output pins
      const outputPins = [this.RST_PIN, this.DC_PIN, this.CS_PIN, this.PWR_PIN];

      for (const pin of outputPins) {
        this.gpioPins[pin] = new Gpio(pin, { mode: Gpio.OUTPUT });
        console.log(`Set GPIO ${pin} to output`);
      }

      // Set up input pin
      this.gpioPins[this.BUSY_PIN] = new Gpio(this.BUSY_PIN, {
        mode: Gpio.INPUT,
      });
      console.log(`Set GPIO ${this.BUSY_PIN} to input`);

      console.log("GPIO pins set up successfully");
    } catch (error) {
      console.error("Failed to setup GPIO:", error);
      throw error;
    }
  }

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

  async delay(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

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
}

module.exports = EPDConfigPigpio;
