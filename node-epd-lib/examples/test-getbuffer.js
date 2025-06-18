#!/usr/bin/env node

const { createCanvas } = require("canvas");
const EPD7in5bV2 = require("../src/epd7in5b-v2");

function testGetBuffer() {
  console.log("Testing getBuffer method...");
  console.log("==========================");

  const epd = new EPD7in5bV2();

  // Test 1: Correct size image
  console.log("\n1. Testing correct size image (800x480)...");
  const canvas1 = createCanvas(800, 480);
  const ctx1 = canvas1.getContext("2d");

  // Draw a simple pattern
  ctx1.fillStyle = "white";
  ctx1.fillRect(0, 0, 800, 480);

  ctx1.fillStyle = "black";
  ctx1.fillRect(100, 100, 200, 200);

  const buffer1 = epd.getBuffer(canvas1);
  console.log(`✅ Buffer created: ${buffer1.length} bytes`);
  console.log(`   Expected size: ${Math.floor(800 / 8) * 480} bytes`);

  // Test 2: Rotated image (480x800)
  console.log("\n2. Testing rotated image (480x800)...");
  const canvas2 = createCanvas(480, 800);
  const ctx2 = canvas2.getContext("2d");

  ctx2.fillStyle = "white";
  ctx2.fillRect(0, 0, 480, 800);

  ctx2.fillStyle = "black";
  ctx2.fillRect(50, 50, 100, 100);

  const buffer2 = epd.getBuffer(canvas2);
  console.log(`✅ Rotated buffer created: ${buffer2.length} bytes`);

  // Test 3: Wrong size image
  console.log("\n3. Testing wrong size image (400x300)...");
  const canvas3 = createCanvas(400, 300);
  const ctx3 = canvas3.getContext("2d");

  ctx3.fillStyle = "white";
  ctx3.fillRect(0, 0, 400, 300);

  const buffer3 = epd.getBuffer(canvas3);
  console.log(
    `✅ Wrong size buffer created: ${buffer3.length} bytes (should be blank)`
  );

  // Test 4: Check buffer content
  console.log("\n4. Checking buffer content...");
  let blackPixels = 0;
  let whitePixels = 0;

  for (let i = 0; i < buffer1.length; i++) {
    for (let bit = 0; bit < 8; bit++) {
      if (buffer1[i] & (1 << (7 - bit))) {
        blackPixels++;
      } else {
        whitePixels++;
      }
    }
  }

  console.log(`   Black pixels: ${blackPixels}`);
  console.log(`   White pixels: ${whitePixels}`);
  console.log(
    `   Total pixels: ${blackPixels + whitePixels} (should be 800*480 = 384000)`
  );

  // Test 5: Test the createBorderedBox method
  console.log("\n5. Testing createBorderedBox method...");
  const borderedBoxBuffer = epd.createBorderedBox();
  console.log(
    `✅ Bordered box buffer created: ${borderedBoxBuffer.length} bytes`
  );

  console.log("\n🎉 All getBuffer tests completed successfully!");
}

// Run the test
testGetBuffer();
