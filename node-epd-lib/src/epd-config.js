const { Gpio } = require("onoff");
const SpiDevice = require("spi-device");

class EPDConfig {
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

    // GPIO objects
    this.gpioRst = null;
    this.gpioDc = null;
    this.gpioCs = null;
    this.gpioPwr = null;
    this.gpioBusy = null;

    // SPI object
    this.spi = null;

    this.initialized = false;
  }

  async init() {
    try {
      console.log("Initializing e-paper hardware...");

      // Initialize GPIO pins
      this.gpioRst = new Gpio(this.RST_PIN, "out");
      this.gpioDc = new Gpio(this.DC_PIN, "out");
      this.gpioCs = new Gpio(this.CS_PIN, "out");
      this.gpioPwr = new Gpio(this.PWR_PIN, "out");
      this.gpioBusy = new Gpio(this.BUSY_PIN, "in", "both");

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

  async digitalWrite(pin, value) {
    if (!this.initialized) {
      throw new Error("EPD not initialized. Call init() first.");
    }

    try {
      switch (pin) {
        case this.RST_PIN:
          await this.gpioRst.write(value ? 1 : 0);
          break;
        case this.DC_PIN:
          await this.gpioDc.write(value ? 1 : 0);
          break;
        case this.CS_PIN:
          await this.gpioCs.write(value ? 1 : 0);
          break;
        case this.PWR_PIN:
          await this.gpioPwr.write(value ? 1 : 0);
          break;
        default:
          throw new Error(`Unknown pin: ${pin}`);
      }
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
      switch (pin) {
        case this.BUSY_PIN:
          return await this.gpioBusy.read();
        default:
          throw new Error(`Unknown pin: ${pin}`);
      }
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

      // Power off and cleanup GPIO
      await this.digitalWrite(this.RST_PIN, 0);
      await this.digitalWrite(this.DC_PIN, 0);
      await this.digitalWrite(this.PWR_PIN, 0);

      // Unexport GPIO pins
      if (this.gpioRst) this.gpioRst.unexport();
      if (this.gpioDc) this.gpioDc.unexport();
      if (this.gpioCs) this.gpioCs.unexport();
      if (this.gpioPwr) this.gpioPwr.unexport();
      if (this.gpioBusy) this.gpioBusy.unexport();

      this.initialized = false;
      console.log("E-paper hardware cleanup completed");
    } catch (error) {
      console.error("Error during cleanup:", error);
    }
  }
}

module.exports = EPDConfig;
