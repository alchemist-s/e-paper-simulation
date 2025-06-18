const SpiDevice = require("spi-device");
const fs = require("fs").promises;
const path = require("path");

class EPDConfigFS {
  constructor() {
    // Pin definitions for 7.5" e-paper display
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

    // SPI object
    this.spi = null;

    this.initialized = false;
  }

  async init() {
    try {
      console.log("Initializing e-paper hardware (file system GPIO)...");

      // Set up GPIO pins using file system
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
      // Export GPIO pins
      const outputPins = [this.RST_PIN, this.DC_PIN, this.CS_PIN, this.PWR_PIN];
      const inputPins = [this.BUSY_PIN];

      // Export all pins
      for (const pin of [...outputPins, ...inputPins]) {
        try {
          await fs.writeFile("/sys/class/gpio/export", pin.toString());
          await this.delay(100); // Wait for export
        } catch (err) {
          // Pin might already be exported, ignore error
        }
      }

      // Set direction for output pins
      for (const pin of outputPins) {
        await fs.writeFile(`/sys/class/gpio/gpio${pin}/direction`, "out");
      }

      // Set direction for input pins
      for (const pin of inputPins) {
        await fs.writeFile(`/sys/class/gpio/gpio${pin}/direction`, "in");
      }

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
      await fs.writeFile(`/sys/class/gpio/gpio${pin}/value`, value ? "1" : "0");
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
      const value = await fs.readFile(
        `/sys/class/gpio/gpio${pin}/value`,
        "utf8"
      );
      return parseInt(value.trim());
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

      // Unexport GPIO pins
      const allPins = [
        this.RST_PIN,
        this.DC_PIN,
        this.CS_PIN,
        this.BUSY_PIN,
        this.PWR_PIN,
      ];
      for (const pin of allPins) {
        try {
          await fs.writeFile("/sys/class/gpio/unexport", pin.toString());
        } catch (err) {
          // Ignore errors during unexport
        }
      }

      this.initialized = false;
      console.log("E-paper hardware cleanup completed");
    } catch (error) {
      console.error("Error during cleanup:", error);
    }
  }
}

module.exports = EPDConfigFS;
