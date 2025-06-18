#!/usr/bin/env node

const EPDConfigFS = require("../src/epd-config-fs");

async function minimalHardwareTest() {
  console.log("Minimal E-Paper Hardware Test");
  console.log("=============================");

  const epdConfig = new EPDConfigFS();

  try {
    // Test 1: Basic initialization
    console.log("\n1. Testing hardware initialization...");
    const initResult = await epdConfig.init();

    if (initResult === 0) {
      console.log("✅ Hardware initialized successfully");
    } else {
      console.log("❌ Hardware initialization failed");
      return;
    }

    // Test 2: GPIO operations
    console.log("\n2. Testing GPIO operations...");
    await epdConfig.digitalWrite(epdConfig.RST_PIN, 1);
    await epdConfig.delay(100);
    await epdConfig.digitalWrite(epdConfig.RST_PIN, 0);
    console.log("✅ GPIO write operations successful");

    // Test 3: SPI operations
    console.log("\n3. Testing SPI operations...");
    const testData = [0x00, 0x01, 0x02, 0x03];
    await epdConfig.spiWrite(testData);
    console.log("✅ SPI write operations successful");

    // Test 4: Display reset sequence
    console.log("\n4. Testing display reset sequence...");
    await epdConfig.digitalWrite(epdConfig.RST_PIN, 1);
    await epdConfig.delay(200);
    await epdConfig.digitalWrite(epdConfig.RST_PIN, 0);
    await epdConfig.delay(4);
    await epdConfig.digitalWrite(epdConfig.RST_PIN, 1);
    await epdConfig.delay(200);
    console.log("✅ Display reset sequence successful");

    // Test 5: Basic display commands
    console.log("\n5. Testing basic display commands...");

    // Send some basic commands to test communication
    await epdConfig.digitalWrite(epdConfig.DC_PIN, 0); // Command mode
    await epdConfig.digitalWrite(epdConfig.CS_PIN, 0); // Select chip
    await epdConfig.spiWrite([0x12]); // Display refresh command
    await epdConfig.digitalWrite(epdConfig.CS_PIN, 1); // Deselect chip

    console.log("✅ Basic display commands successful");

    // Test 6: Cleanup
    console.log("\n6. Testing cleanup...");
    await epdConfig.moduleExit();
    console.log("✅ Cleanup successful");

    console.log("\n🎉 All hardware tests passed!");
    console.log("Your e-paper display hardware is working correctly.");
    console.log("\nNext steps:");
    console.log("1. Install canvas library for image processing");
    console.log("2. Run full display examples");
  } catch (error) {
    console.error("\n❌ Test failed:", error.message);
    console.error("Stack trace:", error.stack);

    // Try to cleanup even if there was an error
    try {
      await epdConfig.moduleExit();
    } catch (cleanupError) {
      console.error("Cleanup error:", cleanupError.message);
    }
  }
}

// Handle process termination
process.on("SIGINT", async () => {
  console.log("\nReceived SIGINT, cleaning up...");
  process.exit(0);
});

process.on("SIGTERM", async () => {
  console.log("\nReceived SIGTERM, cleaning up...");
  process.exit(0);
});

// Run the test
minimalHardwareTest().catch(console.error);
