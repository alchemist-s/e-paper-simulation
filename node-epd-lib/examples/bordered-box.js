#!/usr/bin/env node

const EPD7in5bV2 = require("../src/epd7in5b-v2");

async function main() {
  console.log("Node.js E-Paper Display - Bordered Box Example");
  console.log("==============================================");

  const epd = new EPD7in5bV2();

  try {
    // Initialize the display
    console.log("Initializing display...");
    const initResult = await epd.init();

    if (initResult !== 0) {
      console.error("Failed to initialize display");
      return;
    }

    console.log("Display initialized successfully");

    // Clear the display first
    console.log("Clearing display...");
    await epd.clear();

    // Create a bordered box
    console.log("Creating bordered box...");
    const blackBuffer = epd.createBorderedBox();

    // Create a blank red buffer (no red content for this example)
    const redBuffer = Buffer.alloc(
      Math.floor(epd.WIDTH / 8) * epd.HEIGHT,
      0x00
    );

    // Display the bordered box
    console.log("Displaying bordered box...");
    await epd.display(blackBuffer, redBuffer);

    console.log("Bordered box displayed successfully!");
    console.log(
      "The display should now show a white background with a black border."
    );

    // Wait a bit before sleeping
    console.log("Waiting 5 seconds before putting display to sleep...");
    await new Promise((resolve) => setTimeout(resolve, 5000));

    // Put display to sleep
    console.log("Putting display to sleep...");
    await epd.sleep();

    console.log("Example completed successfully!");
  } catch (error) {
    console.error("Error during execution:", error);

    // Try to cleanup even if there was an error
    try {
      await epd.epdConfig.moduleExit();
    } catch (cleanupError) {
      console.error("Error during cleanup:", cleanupError);
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

// Run the example
main().catch(console.error);
