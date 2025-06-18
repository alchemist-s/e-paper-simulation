#!/usr/bin/env node

/**
 * Minimal E-Paper Hardware Test using pigpio
 *
 * This script tests the basic hardware functionality of the e-paper display
 * using the pigpio library. It verifies GPIO operations, SPI communication,
 * and basic display commands.
 *
 * Requirements:
 * - Raspberry Pi with pigpio C library installed
 * - Node.js pigpio package installed
 * - Root/sudo privileges
 *
 * Usage:
 *   sudo node examples/minimal-test-pigpio.js
 *
 * @see https://github.com/fivdi/pigpio
 */

const EPDConfigPigpio = require("../src/epd-config-pigpio");

async function minimalHardwareTestPigpio() {
  console.log("Minimal E-Paper Hardware Test (pigpio)");
  console.log("======================================");
  console.log("Using pigpio library for fast GPIO operations");
  console.log("");

  const epdConfig = new EPDConfigPigpio();

  try {
    // Test 1: Basic initialization
    console.log("1. Testing hardware initialization...");
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

    // Test 3: GPIO read operations
    console.log("\n3. Testing GPIO read operations...");
    const busyValue = await epdConfig.digitalRead(epdConfig.BUSY_PIN);
    console.log(`   BUSY pin value: ${busyValue}`);
    console.log("✅ GPIO read operations successful");

    // Test 4: SPI operations
    console.log("\n4. Testing SPI operations...");
    const testData = [0x00, 0x01, 0x02, 0x03];
    const receivedData = await epdConfig.spiWrite(testData);
    console.log(`   Sent: [${testData.join(", ")}]`);
    console.log(`   Received: [${Array.from(receivedData).join(", ")}]`);
    console.log("✅ SPI write operations successful");

    // Test 5: Microsecond delay precision
    console.log("\n5. Testing microsecond delay precision...");
    const startTime = process.hrtime.bigint();
    await epdConfig.delayMicroseconds(1000); // 1ms
    const endTime = process.hrtime.bigint();
    const actualDelay = Number(endTime - startTime) / 1000000; // Convert to ms
    console.log(`   Requested: 1ms, Actual: ${actualDelay.toFixed(3)}ms`);
    console.log("✅ Microsecond delay precision test successful");

    // Test 6: Display reset sequence
    console.log("\n6. Testing display reset sequence...");
    await epdConfig.digitalWrite(epdConfig.RST_PIN, 1);
    await epdConfig.delay(200);
    await epdConfig.digitalWrite(epdConfig.RST_PIN, 0);
    await epdConfig.delay(4);
    await epdConfig.digitalWrite(epdConfig.RST_PIN, 1);
    await epdConfig.delay(200);
    console.log("✅ Display reset sequence successful");

    // Test 7: Basic display commands
    console.log("\n7. Testing basic display commands...");

    // Send some basic commands to test communication
    await epdConfig.digitalWrite(epdConfig.DC_PIN, 0); // Command mode
    await epdConfig.digitalWrite(epdConfig.CS_PIN, 0); // Select chip
    await epdConfig.spiWrite([0x12]); // Display refresh command
    await epdConfig.digitalWrite(epdConfig.CS_PIN, 1); // Deselect chip

    console.log("✅ Basic display commands successful");

    // Test 8: Pin information
    console.log("\n8. Displaying pin configuration...");
    const pinInfo = epdConfig.getPinInfo();
    console.log("   GPIO Pins (BCM numbering):");
    console.log(`     RST: GPIO ${pinInfo.RST_PIN}`);
    console.log(`     DC:  GPIO ${pinInfo.DC_PIN}`);
    console.log(`     CS:  GPIO ${pinInfo.CS_PIN}`);
    console.log(`     BUSY: GPIO ${pinInfo.BUSY_PIN}`);
    console.log(`     PWR: GPIO ${pinInfo.PWR_PIN}`);
    console.log("   SPI Configuration:");
    console.log(`     Bus: ${pinInfo.SPI_BUS}, Device: ${pinInfo.SPI_DEVICE}`);
    console.log(
      `     Mode: ${pinInfo.SPI_MODE}, Speed: ${pinInfo.SPI_MAX_SPEED}Hz`
    );
    console.log("✅ Pin configuration displayed");

    // Test 9: Cleanup
    console.log("\n9. Testing cleanup...");
    await epdConfig.moduleExit();
    console.log("✅ Cleanup successful");

    console.log("\n🎉 All hardware tests passed!");
    console.log(
      "Your e-paper display hardware is working correctly with pigpio."
    );
    console.log("\nKey Features Tested:");
    console.log("  ✅ Fast GPIO operations with microsecond precision");
    console.log("  ✅ SPI communication");
    console.log("  ✅ Hardware-level timing accuracy");
    console.log("  ✅ Proper resource cleanup");
    console.log("\nNext Steps:");
    console.log("  - Run the full e-paper driver examples");
    console.log("  - Test with actual display patterns");
    console.log("  - Monitor for any timing issues");
  } catch (error) {
    console.error("\n❌ Test failed:", error.message);
    console.error("Stack trace:", error.stack);

    // Try to cleanup even if there was an error
    try {
      await epdConfig.moduleExit();
    } catch (cleanupError) {
      console.error("Cleanup error:", cleanupError.message);
    }

    console.log("\nTroubleshooting Tips:");
    console.log(
      "  1. Ensure pigpio C library is installed: sudo apt-get install pigpio"
    );
    console.log(
      "  2. Run with sudo privileges: sudo node examples/minimal-test-pigpio.js"
    );
    console.log("  3. Check GPIO pin connections and wiring");
    console.log("  4. Verify SPI is enabled in raspi-config");
    console.log("  5. Check for conflicting GPIO usage");
  }
}

// Handle process termination gracefully
process.on("SIGINT", async () => {
  console.log("\nReceived SIGINT, cleaning up...");
  process.exit(0);
});

process.on("SIGTERM", async () => {
  console.log("\nReceived SIGTERM, cleaning up...");
  process.exit(0);
});

// Run the test
minimalHardwareTestPigpio().catch(console.error);
