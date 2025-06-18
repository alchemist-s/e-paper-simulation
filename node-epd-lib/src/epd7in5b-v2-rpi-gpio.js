const EPDConfigRPiGPIO = require("./epd-config-rpi-gpio");
const { createCanvas } = require("canvas");

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

  getBuffer(image) {
    const img = image;
    const imwidth = img.width;
    const imheight = img.height;

    if (imwidth === this.WIDTH && imheight === this.HEIGHT) {
      // Image is already the correct size
      const canvas = createCanvas(this.WIDTH, this.HEIGHT);
      const ctx = canvas.getContext("2d");
      ctx.drawImage(img, 0, 0);

      // Convert to black and white
      const imageData = ctx.getImageData(0, 0, this.WIDTH, this.HEIGHT);
      const data = imageData.data;

      // Convert to 1-bit per pixel (black/white)
      const buffer = [];
      for (let y = 0; y < this.HEIGHT; y++) {
        for (let x = 0; x < this.WIDTH; x += 8) {
          let byte = 0;
          for (let bit = 0; bit < 8; bit++) {
            if (x + bit < this.WIDTH) {
              const pixelIndex = (y * this.WIDTH + x + bit) * 4;
              const r = data[pixelIndex];
              const g = data[pixelIndex + 1];
              const b = data[pixelIndex + 2];

              // Convert to grayscale and then to black/white
              const gray = (r + g + b) / 3;
              const isBlack = gray < 128;

              if (isBlack) {
                byte |= 1 << (7 - bit);
              }
            }
          }
          buffer.push(byte);
        }
      }

      return buffer;
    } else if (imwidth === this.HEIGHT && imheight === this.WIDTH) {
      // Image needs to be rotated
      const canvas = createCanvas(this.WIDTH, this.HEIGHT);
      const ctx = canvas.getContext("2d");
      ctx.translate(this.WIDTH / 2, this.HEIGHT / 2);
      ctx.rotate(Math.PI / 2);
      ctx.drawImage(img, -imwidth / 2, -imheight / 2);

      // Convert to black and white (same as above)
      const imageData = ctx.getImageData(0, 0, this.WIDTH, this.HEIGHT);
      const data = imageData.data;

      const buffer = [];
      for (let y = 0; y < this.HEIGHT; y++) {
        for (let x = 0; x < this.WIDTH; x += 8) {
          let byte = 0;
          for (let bit = 0; bit < 8; bit++) {
            if (x + bit < this.WIDTH) {
              const pixelIndex = (y * this.WIDTH + x + bit) * 4;
              const r = data[pixelIndex];
              const g = data[pixelIndex + 1];
              const b = data[pixelIndex + 2];

              const gray = (r + g + b) / 3;
              const isBlack = gray < 128;

              if (isBlack) {
                byte |= 1 << (7 - bit);
              }
            }
          }
          buffer.push(byte);
        }
      }

      return buffer;
    } else {
      console.warn(
        `Wrong image dimensions: must be ${this.WIDTH}x${this.HEIGHT}`
      );
      // Return a blank buffer
      return new Array(Math.floor(this.WIDTH / 8) * this.HEIGHT).fill(0x00);
    }
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

  // Helper method to create a bordered box for testing
  createBorderedBox() {
    const canvas = createCanvas(this.WIDTH, this.HEIGHT);
    const ctx = canvas.getContext("2d");

    // Fill with white
    ctx.fillStyle = "white";
    ctx.fillRect(0, 0, this.WIDTH, this.HEIGHT);

    // Draw black border
    ctx.strokeStyle = "black";
    ctx.lineWidth = 10;
    ctx.strokeRect(50, 50, this.WIDTH - 100, this.HEIGHT - 100);

    // Draw some text
    ctx.fillStyle = "black";
    ctx.font = "48px Arial";
    ctx.textAlign = "center";
    ctx.fillText("E-Paper Test", this.WIDTH / 2, this.HEIGHT / 2);

    return this.getBuffer(canvas);
  }

  // Helper method to create an empty (white) buffer
  createEmptyBuffer() {
    return new Array(Math.floor(this.WIDTH / 8) * this.HEIGHT).fill(0x00);
  }
}

module.exports = EPD7in5bV2RPiGPIO;
