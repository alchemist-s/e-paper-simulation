#!/usr/bin/env node

/**
 * E-Paper Display Example using pigpio
 *
 * This example demonstrates how to use the e-paper display library
 * with the pigpio GPIO library for high-performance operations.
 *
 * Requirements:
 * - Raspberry Pi with pigpio C library installed
 * - Node.js pigpio package installed
 * - Root/sudo privileges
 *
 * Usage:
 *   sudo node examples/bordered-box-pigpio.js
 *
 * @see https://github.com/fivdi/pigpio
 */

const { EPD7in5bV2 } = require("../index");

async function displayBorderedBoxPigpio() {
  console.log("E-Paper Display Example (pigpio)");
  console.log("=================================");
  console.log("Using pigpio library for fast GPIO operations");
  console.log("");

  const epd = new EPD7in5bV2();

  try {
    // Initialize the display
    console.log("1. Initializing e-paper display...");
    await epd.init();
    console.log("✅ Display initialized successfully");

    // Clear the display
    console.log("\n2. Clearing display...");
    await epd.clear();
    console.log("✅ Display cleared");

    // Create a bordered box image
    console.log("\n3. Creating bordered box image...");
    const blackBuffer = epd.createBorderedBox();
    const redBuffer = Buffer.alloc(
      Math.floor(epd.WIDTH / 8) * epd.HEIGHT,
      0x00
    );
    console.log("✅ Image created");

    // Display the image
    console.log("\n4. Displaying image...");
    await epd.display(blackBuffer, redBuffer);
    console.log("✅ Image displayed successfully");

    // Wait a moment to see the result
    console.log("\n5. Waiting for display to settle...");
    await epd.delay(2000);

    // Put display to sleep
    console.log("\n6. Putting display to sleep...");
    await epd.sleep();
    console.log("✅ Display put to sleep");

    console.log("\n🎉 Example completed successfully!");
    console.log("You should see a bordered box on your e-paper display.");
    console.log("\nKey Features Demonstrated:");
    console.log("  ✅ Fast GPIO operations with pigpio");
    console.log("  ✅ SPI communication");
    console.log("  ✅ Image buffer creation");
    console.log("  ✅ Display refresh");
    console.log("  ✅ Proper cleanup");
  } catch (error) {
    console.error("\n❌ Error occurred:", error.message);
    console.error("Stack trace:", error.stack);

    // Try to cleanup even if there was an error
    try {
      await epd.sleep();
    } catch (cleanupError) {
      console.error("Cleanup error:", cleanupError.message);
    }

    console.log("\nTroubleshooting Tips:");
    console.log(
      "  1. Ensure pigpio C library is installed: sudo apt-get install pigpio"
    );
    console.log(
      "  2. Run with sudo privileges: sudo node examples/bordered-box-pigpio.js"
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

// Run the example
displayBorderedBoxPigpio().catch(console.error);
