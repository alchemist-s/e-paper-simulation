const EPDConfigRPiGPIO = require("./epd-config-rpi-gpio");

class EPD7in5bV2RPiGPIO {
  constructor() {
    this.epdConfig = new EPDConfigRPiGPIO();

    // Display resolution
    this.WIDTH = 800;
    this.HEIGHT = 480;

    // Pin references
    this.resetPin = this.epdConfig.RST_PIN;
    this.dcPin = this.epdConfig.DC_PIN;
    this.busyPin = this.epdConfig.BUSY_PIN;
    this.csPin = this.epdConfig.CS_PIN;

    this.partFlag = 1;
  }

  async init() {
    if (this.epdConfig.moduleInit() !== 0) {
      return -1;
    }

    // EPD hardware init start
    await this.reset();

    await this.sendCommand(0x01);
    await this.sendData(0x07);
    await this.sendData(0x07);
    await this.sendData(0x3f);
    await this.sendData(0x3f);

    await this.sendCommand(0x06);
    await this.sendData(0x17);
    await this.sendData(0x17);
    await this.sendData(0x28);
    await this.sendData(0x17);

    await this.sendCommand(0x04);
    await this.epdConfig.delay(100);
    await this.readBusy();

    await this.sendCommand(0x00);
    await this.sendData(0x0f);

    await this.sendCommand(0x61);
    await this.sendData(0x03);
    await this.sendData(0x20);
    await this.sendData(0x01);
    await this.sendData(0xe0);

    await this.sendCommand(0x15);
    await this.sendData(0x00);

    await this.sendCommand(0x50);
    await this.sendData(0x11);
    await this.sendData(0x07);

    await this.sendCommand(0x60);
    await this.sendData(0x22);

    return 0;
  }

  async initFast() {
    if (this.epdConfig.moduleInit() !== 0) {
      return -1;
    }

    // EPD hardware init start
    await this.reset();

    await this.sendCommand(0x00);
    await this.sendData(0x0f);

    await this.sendCommand(0x04);
    await this.epdConfig.delay(100);
    await this.readBusy();

    await this.sendCommand(0x06);
    await this.sendData(0x27);
    await this.sendData(0x27);
    await this.sendData(0x18);
    await this.sendData(0x17);

    await this.sendCommand(0xe0);
    await this.sendData(0x02);
    await this.sendCommand(0xe5);
    await this.sendData(0x5a);

    await this.sendCommand(0x50);
    await this.sendData(0x11);
    await this.sendData(0x07);

    return 0;
  }

  async initPart() {
    if (this.epdConfig.moduleInit() !== 0) {
      return -1;
    }

    // EPD hardware init start
    await this.reset();

    await this.sendCommand(0x00);
    await this.sendData(0x1f);

    await this.sendCommand(0x04);
    await this.epdConfig.delay(100);
    await this.readBusy();

    await this.sendCommand(0xe0);
    await this.sendData(0x02);
    await this.sendCommand(0xe5);
    await this.sendData(0x6e);

    await this.sendCommand(0x50);
    await this.sendData(0xa9);
    await this.sendData(0x07);

    return 0;
  }

  async reset() {
    await this.epdConfig.digitalWrite(this.resetPin, 1);
    await this.epdConfig.delay(200);
    await this.epdConfig.digitalWrite(this.resetPin, 0);
    await this.epdConfig.delay(4);
    await this.epdConfig.digitalWrite(this.resetPin, 1);
    await this.epdConfig.delay(200);
  }

  async sendCommand(command) {
    await this.epdConfig.digitalWrite(this.dcPin, 0);
    await this.epdConfig.digitalWrite(this.csPin, 0);
    await this.epdConfig.spiWrite([command]);
    await this.epdConfig.digitalWrite(this.csPin, 1);
  }

  async sendData(data) {
    await this.epdConfig.digitalWrite(this.dcPin, 1);
    await this.epdConfig.digitalWrite(this.csPin, 0);
    await this.epdConfig.spiWrite([data]);
    await this.epdConfig.digitalWrite(this.csPin, 1);
  }

  async sendData2(data) {
    await this.epdConfig.digitalWrite(this.dcPin, 1);
    await this.epdConfig.digitalWrite(this.csPin, 0);
    await this.epdConfig.spiWrite(data);
    await this.epdConfig.digitalWrite(this.csPin, 1);
  }

  async readBusy() {
    console.log("e-Paper busy");
    await this.sendCommand(0x71);
    let busy = await this.epdConfig.digitalRead(this.busyPin);
    while (busy === 0) {
      await this.sendCommand(0x71);
      busy = await this.epdConfig.digitalRead(this.busyPin);
    }
    await this.epdConfig.delay(200);
    console.log("e-Paper busy release");
  }

  // Simple method to create a bordered box without canvas
  createBorderedBox() {
    const bufferSize = Math.floor(this.WIDTH / 8) * this.HEIGHT;
    const buffer = new Array(bufferSize).fill(0x00); // Start with all white

    // Calculate border positions
    const borderWidth = 10;
    const margin = 50;

    // Draw horizontal borders
    for (let y = margin; y < margin + borderWidth; y++) {
      for (let x = margin; x < this.WIDTH - margin; x++) {
        const byteIndex = Math.floor((y * this.WIDTH) / 8) + Math.floor(x / 8);
        const bitPosition = 7 - (x % 8);
        buffer[byteIndex] |= 1 << bitPosition;
      }
    }

    for (
      let y = this.HEIGHT - margin - borderWidth;
      y < this.HEIGHT - margin;
      y++
    ) {
      for (let x = margin; x < this.WIDTH - margin; x++) {
        const byteIndex = Math.floor((y * this.WIDTH) / 8) + Math.floor(x / 8);
        const bitPosition = 7 - (x % 8);
        buffer[byteIndex] |= 1 << bitPosition;
      }
    }

    // Draw vertical borders
    for (let x = margin; x < margin + borderWidth; x++) {
      for (let y = margin; y < this.HEIGHT - margin; y++) {
        const byteIndex = Math.floor((y * this.WIDTH) / 8) + Math.floor(x / 8);
        const bitPosition = 7 - (x % 8);
        buffer[byteIndex] |= 1 << bitPosition;
      }
    }

    for (
      let x = this.WIDTH - margin - borderWidth;
      x < this.WIDTH - margin;
      x++
    ) {
      for (let y = margin; y < this.HEIGHT - margin; y++) {
        const byteIndex = Math.floor((y * this.WIDTH) / 8) + Math.floor(x / 8);
        const bitPosition = 7 - (x % 8);
        buffer[byteIndex] |= 1 << bitPosition;
      }
    }

    // Draw simple text pattern (just some black pixels in the center)
    const centerX = Math.floor(this.WIDTH / 2);
    const centerY = Math.floor(this.HEIGHT / 2);

    // Draw a simple "X" pattern
    for (let i = 0; i < 100; i++) {
      const x1 = centerX - 50 + i;
      const y1 = centerY - 50 + i;
      const x2 = centerX + 50 - i;
      const y2 = centerY - 50 + i;

      if (x1 >= 0 && x1 < this.WIDTH && y1 >= 0 && y1 < this.HEIGHT) {
        const byteIndex =
          Math.floor((y1 * this.WIDTH) / 8) + Math.floor(x1 / 8);
        const bitPosition = 7 - (x1 % 8);
        buffer[byteIndex] |= 1 << bitPosition;
      }

      if (x2 >= 0 && x2 < this.WIDTH && y2 >= 0 && y2 < this.HEIGHT) {
        const byteIndex =
          Math.floor((y2 * this.WIDTH) / 8) + Math.floor(x2 / 8);
        const bitPosition = 7 - (x2 % 8);
        buffer[byteIndex] |= 1 << bitPosition;
      }
    }

    return buffer;
  }

  // Method to create a simple pattern
  createPattern(pattern = "checkerboard") {
    const bufferSize = Math.floor(this.WIDTH / 8) * this.HEIGHT;
    const buffer = new Array(bufferSize).fill(0x00);

    if (pattern === "checkerboard") {
      for (let y = 0; y < this.HEIGHT; y++) {
        for (let x = 0; x < this.WIDTH; x += 8) {
          const byteIndex =
            Math.floor((y * this.WIDTH) / 8) + Math.floor(x / 8);
          if ((y + Math.floor(x / 8)) % 2 === 0) {
            buffer[byteIndex] = 0xaa; // 10101010
          } else {
            buffer[byteIndex] = 0x55; // 01010101
          }
        }
      }
    } else if (pattern === "stripes") {
      for (let y = 0; y < this.HEIGHT; y++) {
        for (let x = 0; x < this.WIDTH; x += 8) {
          const byteIndex =
            Math.floor((y * this.WIDTH) / 8) + Math.floor(x / 8);
          if (y % 20 < 10) {
            buffer[byteIndex] = 0xff; // All black
          } else {
            buffer[byteIndex] = 0x00; // All white
          }
        }
      }
    } else if (pattern === "dots") {
      for (let y = 0; y < this.HEIGHT; y += 20) {
        for (let x = 0; x < this.WIDTH; x += 20) {
          // Draw a small dot
          for (let dy = 0; dy < 5; dy++) {
            for (let dx = 0; dx < 5; dx++) {
              const px = x + dx;
              const py = y + dy;
              if (px < this.WIDTH && py < this.HEIGHT) {
                const byteIndex =
                  Math.floor((py * this.WIDTH) / 8) + Math.floor(px / 8);
                const bitPosition = 7 - (px % 8);
                buffer[byteIndex] |= 1 << bitPosition;
              }
            }
          }
        }
      }
    }

    return buffer;
  }

  async display(imageBlack, imageRed) {
    await this.sendCommand(0x10);

    // The black bytes need to be inverted back from what getBuffer did
    const invertedBlack = imageBlack.map((byte) => byte ^ 0xff);
    await this.sendData2(invertedBlack);

    await this.sendCommand(0x13);
    await this.sendData2(imageRed);

    await this.sendCommand(0x12);
    await this.epdConfig.delay(100);
    await this.readBusy();
  }

  async displayPartial(image, xStart, yStart, xEnd, yEnd) {
    const width = xEnd - xStart;
    const height = yEnd - yStart;

    await this.sendCommand(0x91);
    await this.sendCommand(0x90);
    await this.sendData(xStart);
    await this.sendData(xStart >> 8);
    await this.sendData(xEnd - 1);
    await this.sendData((xEnd - 1) >> 8);
    await this.sendData(yStart);
    await this.sendData(yStart >> 8);
    await this.sendData(yEnd - 1);
    await this.sendData((yEnd - 1) >> 8);
    await this.sendData(0x01);

    if (this.partFlag === 1) {
      this.partFlag = 0;
      await this.sendCommand(0x10);
      for (let j = 0; j < height; j++) {
        for (let i = 0; i < width; i++) {
          await this.sendData(0xff);
        }
      }
    }

    await this.sendCommand(0x13);
    await this.sendData2(image);

    await this.sendCommand(0x12);
    await this.epdConfig.delay(100);
    await this.readBusy();
  }

  async clear() {
    const buf = new Array(Math.floor(this.WIDTH / 8) * this.HEIGHT).fill(0x00);
    const buf2 = new Array(Math.floor(this.WIDTH / 8) * this.HEIGHT).fill(0xff);

    await this.sendCommand(0x10);
    await this.sendData2(buf2);

    await this.sendCommand(0x13);
    await this.sendData2(buf);

    await this.sendCommand(0x12);
    await this.epdConfig.delay(100);
    await this.readBusy();
  }

  async sleep() {
    await this.sendCommand(0x02); // POWER_OFF
    await this.readBusy();

    await this.sendCommand(0x07); // DEEP_SLEEP
    await this.sendData(0xa5);

    await this.epdConfig.delay(2000);
    await this.epdConfig.moduleExit();
  }

  // Helper method to create an empty (white) buffer
  createEmptyBuffer() {
    return new Array(Math.floor(this.WIDTH / 8) * this.HEIGHT).fill(0x00);
  }
}

module.exports = EPD7in5bV2RPiGPIO;
