#!/usr/bin/env node

const EPD7in5bV2RPiGPIO = require("../src/epd7in5b-v2-rpi-gpio");

async function displayBorderedBox() {
  console.log("E-Paper Bordered Box Test (RPi GPIO)");
  console.log("=====================================");

  const epd = new EPD7in5bV2RPiGPIO();

  try {
    // Initialize the display
    console.log("\n1. Initializing display...");
    const initResult = await epd.init();

    if (initResult === 0) {
      console.log("✅ Display initialized successfully");
    } else {
      console.log("❌ Display initialization failed");
      return;
    }

    // Create the bordered box image
    console.log("\n2. Creating bordered box image...");
    const blackBuffer = epd.createBorderedBox();
    const redBuffer = epd.createEmptyBuffer();

    console.log("✅ Image created successfully");
    console.log(`   Black buffer size: ${blackBuffer.length} bytes`);
    console.log(`   Red buffer size: ${redBuffer.length} bytes`);

    // Display the image
    console.log("\n3. Displaying image...");
    await epd.display(blackBuffer, redBuffer);
    console.log("✅ Image displayed successfully");

    // Wait a moment to see the result
    console.log("\n4. Waiting 5 seconds...");
    await epd.epdConfig.delay(5000);

    // Clear the display
    console.log("\n5. Clearing display...");
    await epd.clear();
    console.log("✅ Display cleared successfully");

    // Put display to sleep
    console.log("\n6. Putting display to sleep...");
    await epd.sleep();
    console.log("✅ Display put to sleep successfully");

    console.log("\n🎉 Test completed successfully!");
    console.log(
      "You should have seen a bordered box with text on your e-paper display."
    );
  } catch (error) {
    console.error("\n❌ Test failed:", error.message);
    console.error("Stack trace:", error.stack);

    // Try to cleanup even if there was an error
    try {
      await epd.sleep();
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
displayBorderedBox().catch(console.error);
