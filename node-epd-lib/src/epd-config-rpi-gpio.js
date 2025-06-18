const SpiDevice = require("spi-device");

class EPDConfigRPiGPIO {
  constructor() {
    // Pin definitions for 7.5" e-paper display (Raspberry Pi BCM numbering)
    this.RST_PIN = 17;
    this.DC_PIN = 25;
    this.CS_PIN = 8;
    this.BUSY_PIN = 24;
    this.PWR_PIN = 18;

    // SPI configuration
    this.SPI_BUS = 0;
    this.SPI_DEVICE = 0;
    this.SPI_MODE = 0;
    this.SPI_MAX_SPEED = 4000000; // 4MHz

    // GPIO and SPI objects
    this.gpio = null;
    this.spi = null;

    this.initialized = false;
  }

  async init() {
    try {
      console.log("Initializing e-paper hardware (RPi GPIO)...");

      // Initialize GPIO using rpi-gpio
      this.gpio = require("rpi-gpio");

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
    return new Promise((resolve, reject) => {
      // Set GPIO mode to BCM (GPIO numbering)
      this.gpio.setMode(this.gpio.MODE_BCM);

      // Setup output pins
      const outputPins = [this.RST_PIN, this.DC_PIN, this.CS_PIN, this.PWR_PIN];
      let setupCount = 0;

      outputPins.forEach((pin) => {
        this.gpio.setup(pin, this.gpio.DIR_OUT, (err) => {
          if (err) {
            console.error(`Failed to setup GPIO pin ${pin}:`, err);
            reject(err);
            return;
          }
          setupCount++;
          if (setupCount === outputPins.length) {
            // Setup input pin
            this.gpio.setup(this.BUSY_PIN, this.gpio.DIR_IN, (err) => {
              if (err) {
                console.error(
                  `Failed to setup GPIO pin ${this.BUSY_PIN}:`,
                  err
                );
                reject(err);
                return;
              }
              resolve();
            });
          }
        });
      });
    });
  }

  async digitalWrite(pin, value) {
    if (!this.initialized) {
      throw new Error("EPD not initialized. Call init() first.");
    }

    return new Promise((resolve, reject) => {
      this.gpio.write(pin, value, (err) => {
        if (err) {
          console.error(`Failed to write to pin ${pin}:`, err);
          reject(err);
        } else {
          resolve();
        }
      });
    });
  }

  async digitalRead(pin) {
    if (!this.initialized) {
      throw new Error("EPD not initialized. Call init() first.");
    }

    return new Promise((resolve, reject) => {
      this.gpio.read(pin, (err, value) => {
        if (err) {
          console.error(`Failed to read from pin ${pin}:`, err);
          reject(err);
        } else {
          resolve(value);
        }
      });
    });
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

      // Reset GPIO mode
      this.gpio.reset();

      this.initialized = false;
      console.log("E-paper hardware cleanup completed");
    } catch (error) {
      console.error("Error during cleanup:", error);
    }
  }
}

module.exports = EPDConfigRPiGPIO;
