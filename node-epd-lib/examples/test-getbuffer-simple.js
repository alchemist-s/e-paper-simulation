#!/usr/bin/env node

const EPD7in5bV2 = require("../src/epd7in5b-v2");

function testGetBufferLogic() {
  console.log("Testing getBuffer logic (without canvas)...");
  console.log("==========================================");

  const epd = new EPD7in5bV2();

  // Test 1: Check buffer size calculation
  console.log("\n1. Testing buffer size calculation...");
  const expectedSize = Math.floor(epd.WIDTH / 8) * epd.HEIGHT;
  console.log(`   Display size: ${epd.WIDTH}x${epd.HEIGHT}`);
  console.log(`   Expected buffer size: ${expectedSize} bytes`);
  console.log(`   Pixels per byte: 8`);
  console.log(`   Total pixels: ${epd.WIDTH * epd.HEIGHT}`);

  // Test 2: Create a mock canvas-like object
  console.log("\n2. Testing with mock canvas object...");
  const mockCanvas = {
    width: 800,
    height: 480,
    getImageData: function (x, y, width, height) {
      // Create a simple test pattern
      const data = new Uint8ClampedArray(width * height * 4);

      for (let i = 0; i < data.length; i += 4) {
        const pixelIndex = i / 4;
        const pixelX = pixelIndex % width;
        const pixelY = Math.floor(pixelIndex / width);

        // Create a simple pattern: black border, white center
        if (
          pixelX < 50 ||
          pixelX >= width - 50 ||
          pixelY < 50 ||
          pixelY >= height - 50
        ) {
          // Black border
          data[i] = 0; // R
          data[i + 1] = 0; // G
          data[i + 2] = 0; // B
          data[i + 3] = 255; // A
        } else {
          // White center
          data[i] = 255; // R
          data[i + 1] = 255; // G
          data[i + 2] = 255; // B
          data[i + 3] = 255; // A
        }
      }

      return { data: data };
    },
  };

  try {
    const buffer = epd.getBuffer(mockCanvas);
    console.log(`✅ Buffer created: ${buffer.length} bytes`);

    // Test 3: Analyze buffer content
    console.log("\n3. Analyzing buffer content...");
    let blackPixels = 0;
    let whitePixels = 0;

    for (let i = 0; i < buffer.length; i++) {
      for (let bit = 0; bit < 8; bit++) {
        if (buffer[i] & (1 << (7 - bit))) {
          blackPixels++;
        } else {
          whitePixels++;
        }
      }
    }

    console.log(`   Black pixels: ${blackPixels}`);
    console.log(`   White pixels: ${whitePixels}`);
    console.log(`   Total pixels: ${blackPixels + whitePixels}`);
    console.log(`   Expected total: ${epd.WIDTH * epd.HEIGHT}`);

    // Test 4: Check first few bytes
    console.log("\n4. Checking first few buffer bytes...");
    for (let i = 0; i < Math.min(10, buffer.length); i++) {
      console.log(`   Byte ${i}: 0x${buffer[i].toString(16).padStart(2, "0")}`);
    }

    console.log("\n🎉 getBuffer logic test completed successfully!");
  } catch (error) {
    console.error("❌ Error testing getBuffer:", error.message);
  }
}

// Run the test
testGetBufferLogic();
