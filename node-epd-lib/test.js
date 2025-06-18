#!/usr/bin/env node

const { EPDConfig, EPD7in5bV2 } = require("./index");

async function testHardware() {
  console.log("Node.js E-Paper Hardware Test");
  console.log("=============================");
  console.log();

  let epdConfig = null;
  let epd = null;

  try {
    // Test 1: Basic EPDConfig initialization
    console.log("1. Testing EPDConfig initialization...");
    epdConfig = new EPDConfig();
    console.log("✅ EPDConfig created successfully");

    // Test 2: Hardware initialization
    console.log("\n2. Testing hardware initialization...");
    const initResult = await epdConfig.init();
    if (initResult === 0) {
      console.log("✅ Hardware initialized successfully");
    } else {
      console.log("❌ Hardware initialization failed");
      return false;
    }

    // Test 3: GPIO operations
    console.log("\n3. Testing GPIO operations...");
    await epdConfig.digitalWrite(epdConfig.RST_PIN, 1);
    await epdConfig.delay(100);
    await epdConfig.digitalWrite(epdConfig.RST_PIN, 0);
    console.log("✅ GPIO write operations successful");

    // Test 4: SPI operations
    console.log("\n4. Testing SPI operations...");
    const testData = [0x00, 0x01, 0x02, 0x03];
    await epdConfig.spiWrite(testData);
    console.log("✅ SPI write operations successful");

    // Test 5: EPD7in5bV2 initialization
    console.log("\n5. Testing EPD7in5bV2 initialization...");
    epd = new EPD7in5bV2();
    const epdInitResult = await epd.init();
    if (epdInitResult === 0) {
      console.log("✅ EPD7in5bV2 initialized successfully");
    } else {
      console.log("❌ EPD7in5bV2 initialization failed");
      return false;
    }

    // Test 6: Display operations
    console.log("\n6. Testing display operations...");
    await epd.clear();
    console.log("✅ Display clear operation successful");

    // Test 7: Image creation
    console.log("\n7. Testing image creation...");
    const blackBuffer = epd.createBorderedBox();
    console.log(`✅ Bordered box created (${blackBuffer.length} bytes)`);

    // Test 8: Display update
    console.log("\n8. Testing display update...");
    const redBuffer = Buffer.alloc(
      Math.floor(epd.WIDTH / 8) * epd.HEIGHT,
      0x00
    );
    await epd.display(blackBuffer, redBuffer);
    console.log("✅ Display update successful");

    // Test 9: Sleep mode
    console.log("\n9. Testing sleep mode...");
    await epd.sleep();
    console.log("✅ Sleep mode successful");

    console.log("\n🎉 All tests passed! Hardware is working correctly.");
    return true;
  } catch (error) {
    console.error("\n❌ Test failed:", error.message);

    // Try to cleanup
    try {
      if (epd) {
        await epd.sleep();
      } else if (epdConfig) {
        await epdConfig.moduleExit();
      }
    } catch (cleanupError) {
      console.error("Cleanup error:", cleanupError.message);
    }

    return false;
  }
}

async function testSimulation() {
  console.log("Node.js E-Paper Simulation Test");
  console.log("===============================");
  console.log();

  try {
    // Test canvas creation
    console.log("1. Testing canvas creation...");
    const { createCanvas } = require("canvas");
    const canvas = createCanvas(800, 480);
    const ctx = canvas.getContext("2d");

    // Draw a test pattern
    ctx.fillStyle = "white";
    ctx.fillRect(0, 0, 800, 480);

    ctx.fillStyle = "black";
    ctx.strokeStyle = "black";
    ctx.lineWidth = 5;
    ctx.strokeRect(50, 50, 700, 380);

    ctx.font = "48px Arial";
    ctx.fillText("Test Pattern", 300, 240);

    console.log("✅ Canvas creation and drawing successful");

    // Test buffer conversion
    console.log("\n2. Testing buffer conversion...");
    const imageData = ctx.getImageData(0, 0, 800, 480);
    const buffer = Buffer.alloc(Math.floor(800 / 8) * 480);

    for (let y = 0; y < 480; y++) {
      for (let x = 0; x < 800; x++) {
        const pixelIndex = (y * 800 + x) * 4;
        const r = imageData.data[pixelIndex];
        const g = imageData.data[pixelIndex + 1];
        const b = imageData.data[pixelIndex + 2];

        const isBlack = (r + g + b) / 3 < 128;

        if (isBlack) {
          const byteIndex = Math.floor((y * 800 + x) / 8);
          const bitIndex = 7 - ((y * 800 + x) % 8);
          buffer[byteIndex] |= 1 << bitIndex;
        }
      }
    }

    console.log(`✅ Buffer conversion successful (${buffer.length} bytes)`);
    console.log("\n🎉 Simulation tests passed!");
    return true;
  } catch (error) {
    console.error("\n❌ Simulation test failed:", error.message);
    return false;
  }
}

async function main() {
  console.log("Node.js E-Paper Library Test Suite");
  console.log("==================================");
  console.log();

  // Check if we're on a Raspberry Pi
  const fs = require("fs");
  const isRaspberryPi =
    fs.existsSync("/proc/cpuinfo") &&
    fs.readFileSync("/proc/cpuinfo", "utf8").includes("Raspberry");

  if (isRaspberryPi) {
    console.log("Raspberry Pi detected - running hardware tests...\n");
    const hardwareResult = await testHardware();

    if (!hardwareResult) {
      console.log("\n⚠️  Hardware tests failed, but this might be normal if:");
      console.log("   - Hardware is not connected");
      console.log("   - Permissions are not set correctly");
      console.log("   - SPI is not enabled");
    }
  } else {
    console.log("Not on Raspberry Pi - running simulation tests...\n");
    await testSimulation();
  }

  console.log("\nTest suite completed!");
}

// Handle process termination
process.on("SIGINT", () => {
  console.log("\nReceived SIGINT, exiting...");
  process.exit(0);
});

process.on("SIGTERM", () => {
  console.log("\nReceived SIGTERM, exiting...");
  process.exit(0);
});

// Run the tests
main().catch(console.error);
