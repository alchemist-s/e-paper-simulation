const EPDConfig = require("./epd-config");

class EPD7in5bV2 {
  constructor() {
    this.epdConfig = new EPDConfig();

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
    if ((await this.epdConfig.init()) !== 0) {
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
    // Convert image to 1-bit buffer
    let img = image;
    const imwidth = img.width;
    const imheight = img.height;

    if (imwidth === this.WIDTH && imheight === this.HEIGHT) {
      // Image is already correct size
      // Convert to 1-bit (black and white)
      img = this.convertTo1Bit(img);
    } else if (imwidth === this.HEIGHT && imheight === this.WIDTH) {
      // Image has correct dimensions, but needs to be rotated
      img = this.rotateImage(img, 90);
      img = this.convertTo1Bit(img);
    } else {
      console.warn(
        `Wrong image dimensions: must be ${this.WIDTH}x${this.HEIGHT}`
      );
      // Return a blank buffer
      return Buffer.alloc(Math.floor(this.WIDTH / 8) * this.HEIGHT, 0x00);
    }

    // Convert canvas to raw bytes
    const imageData = img.getImageData(0, 0, this.WIDTH, this.HEIGHT);
    const rawBytes = Buffer.from(imageData.data);

    // Convert to 1-bit buffer (8 pixels per byte)
    const buffer = Buffer.alloc(Math.floor(this.WIDTH / 8) * this.HEIGHT);

    for (let y = 0; y < this.HEIGHT; y++) {
      for (let x = 0; x < this.WIDTH; x++) {
        const pixelIndex = (y * this.WIDTH + x) * 4;
        const r = rawBytes[pixelIndex];
        const g = rawBytes[pixelIndex + 1];
        const b = rawBytes[pixelIndex + 2];

        // Convert to black/white (0=black, 1=white in PIL world)
        const isWhite = (r + g + b) / 3 >= 128;

        if (isWhite) {
          const byteIndex = Math.floor((y * this.WIDTH + x) / 8);
          const bitIndex = 7 - ((y * this.WIDTH + x) % 8);
          buffer[byteIndex] |= 1 << bitIndex;
        }
      }
    }

    // The bytes need to be inverted, because in the PIL world 0=black and 1=white, but
    // in the e-paper world 0=white and 1=black.
    for (let i = 0; i < buffer.length; i++) {
      buffer[i] ^= 0xff;
    }

    return buffer;
  }

  convertTo1Bit(canvas) {
    const { createCanvas } = require("canvas");
    const newCanvas = createCanvas(this.WIDTH, this.HEIGHT);
    const ctx = newCanvas.getContext("2d");

    // Draw the original image
    ctx.drawImage(canvas, 0, 0);

    // Get image data and convert to 1-bit
    const imageData = ctx.getImageData(0, 0, this.WIDTH, this.HEIGHT);
    const data = imageData.data;

    for (let i = 0; i < data.length; i += 4) {
      const r = data[i];
      const g = data[i + 1];
      const b = data[i + 2];

      // Convert to grayscale and then to black/white
      const gray = (r + g + b) / 3;
      const bw = gray >= 128 ? 255 : 0;

      data[i] = bw; // R
      data[i + 1] = bw; // G
      data[i + 2] = bw; // B
      // Alpha stays the same
    }

    ctx.putImageData(imageData, 0, 0);
    return newCanvas;
  }

  rotateImage(canvas, degrees) {
    const { createCanvas } = require("canvas");
    const newCanvas = createCanvas(this.WIDTH, this.HEIGHT);
    const ctx = newCanvas.getContext("2d");

    // Save context
    ctx.save();

    // Move to center of canvas
    ctx.translate(this.WIDTH / 2, this.HEIGHT / 2);

    // Rotate
    ctx.rotate((degrees * Math.PI) / 180);

    // Draw the rotated image
    ctx.drawImage(canvas, -canvas.width / 2, -canvas.height / 2);

    // Restore context
    ctx.restore();

    return newCanvas;
  }

  async display(imageBlack, imageRed) {
    await this.sendCommand(0x10);

    // Invert black bytes (same as Python implementation)
    const blackBuffer = Buffer.from(imageBlack);
    for (let i = 0; i < blackBuffer.length; i++) {
      blackBuffer[i] ^= 0xff;
    }
    await this.sendData2(blackBuffer);

    await this.sendCommand(0x13);
    await this.sendData2(imageRed);

    await this.sendCommand(0x12);
    await this.epdConfig.delay(100);
    await this.readBusy();
  }

  async clear() {
    const buf = Buffer.alloc(Math.floor(this.WIDTH / 8) * this.HEIGHT, 0x00);
    const buf2 = Buffer.alloc(Math.floor(this.WIDTH / 8) * this.HEIGHT, 0xff);

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

  async init_Fast() {
    if ((await this.epdConfig.init()) !== 0) {
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

  async init_part() {
    if ((await this.epdConfig.init()) !== 0) {
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

    // EPD hardware init end
    return 0;
  }

  async display_Base_color(color) {
    let width;
    if (this.WIDTH % 8 === 0) {
      width = Math.floor(this.WIDTH / 8);
    } else {
      width = Math.floor(this.WIDTH / 8) + 1;
    }
    const height = this.HEIGHT;

    await this.sendCommand(0x10); // Write Black and White image to RAM
    for (let j = 0; j < height; j++) {
      for (let i = 0; i < width; i++) {
        await this.sendData(color);
      }
    }

    await this.sendCommand(0x13); // Write Black and White image to RAM
    for (let j = 0; j < height; j++) {
      for (let i = 0; i < width; i++) {
        await this.sendData(~color);
      }
    }

    await this.sendCommand(0x12);
    await this.epdConfig.delay(100);
    await this.readBusy();
  }

  async display_Partial(image, xStart, yStart, xEnd, yEnd) {
    let adjustedXStart = xStart;
    let adjustedXEnd = xEnd;

    if (
      ((xStart % 8) + (xEnd % 8) === 8 && xStart % 8 > xEnd % 8) ||
      (xStart % 8) + (xEnd % 8) === 0 ||
      (xEnd - xStart) % 8 === 0
    ) {
      adjustedXStart = Math.floor(xStart / 8) * 8;
      adjustedXEnd = Math.floor(xEnd / 8) * 8;
    } else {
      adjustedXStart = Math.floor(xStart / 8) * 8;
      if (xEnd % 8 === 0) {
        adjustedXEnd = Math.floor(xEnd / 8) * 8;
      } else {
        adjustedXEnd = Math.floor(xEnd / 8) * 8 + 1;
      }
    }

    const width = Math.floor((adjustedXEnd - adjustedXStart) / 8);
    const height = yEnd - yStart;

    await this.sendCommand(0x91); // This command makes the display enter partial mode
    await this.sendCommand(0x90); // resolution setting
    await this.sendData(Math.floor(adjustedXStart / 256));
    await this.sendData(adjustedXStart % 256); // x-start

    await this.sendData(Math.floor((adjustedXEnd - 1) / 256));
    await this.sendData((adjustedXEnd - 1) % 256); // x-end

    await this.sendData(Math.floor(yStart / 256));
    await this.sendData(yStart % 256); // y-start

    await this.sendData(Math.floor((yEnd - 1) / 256));
    await this.sendData((yEnd - 1) % 256); // y-end
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

    await this.sendCommand(0x13); // Write Black and White image to RAM
    await this.sendData2(image);

    await this.sendCommand(0x12);
    await this.epdConfig.delay(100);
    await this.readBusy();
  }

  // Helper method to create a simple bordered box
  createBorderedBox() {
    const { createCanvas } = require("canvas");
    const canvas = createCanvas(this.WIDTH, this.HEIGHT);
    const ctx = canvas.getContext("2d");

    // Fill with white background
    ctx.fillStyle = "white";
    ctx.fillRect(0, 0, this.WIDTH, this.HEIGHT);

    // Draw black border
    ctx.strokeStyle = "black";
    ctx.lineWidth = 10;
    ctx.strokeRect(50, 50, this.WIDTH - 100, this.HEIGHT - 100);

    // Use the getBuffer method to convert to proper format
    return this.getBuffer(canvas);
  }
}

module.exports = EPD7in5bV2;
