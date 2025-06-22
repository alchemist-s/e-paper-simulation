<template>
  <div class="app">
    <div class="canvas-container">
      <!-- PixiJS Canvas -->
      <canvas ref="canvasRef"></canvas>
      <!-- Debug Image -->
      <img
        v-if="debugImage"
        :src="debugImage"
        alt="Debug Image"
        class="debug-image"
      />
      <!-- Controls -->
      <div class="controls">
        <button @click="changeText" class="btn">Change Text</button>
        <button @click="sendRegionsToServer" class="btn">Send Regions</button>
        <button @click="sendFullImage" class="btn">Send Full Image</button>
      </div>
      <!-- Debug Info -->
      <div class="debug-info">
        <p>Regions detected: {{ regions.length }}</p>
        <p>Last update: {{ lastUpdateTime }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Application, Text, Container } from "pixi.js";
import { ref, onMounted } from "vue";

const canvasRef = ref<HTMLCanvasElement | null>(null);
const serverUrl = ref<string>("http://192.168.1.111:8000");
const pixiApp = ref<Application | null>(null);
const textToDisplay = ref<string>("Hello PixiJS!");
const debugImage = ref<string>("");
const regions = ref<
  Array<{
    x: number;
    y: number;
    width: number;
    height: number;
    imageData: string;
  }>
>([]);
const lastUpdateTime = ref<string>("");
let textRef: Text | null = null;
let previousCanvasData: ImageData | null = null;

// Function to detect changed regions between two canvas states
const detectChangedRegions = (
  currentData: ImageData,
  previousData: ImageData | null
): Array<{
  x: number;
  y: number;
  width: number;
  height: number;
  imageData: string;
}> => {
  if (!previousData) {
    // First update - return full canvas as one region
    return [
      {
        x: 0,
        y: 0,
        width: currentData.width,
        height: currentData.height,
        imageData: canvasRef.value!.toDataURL("image/png"),
      },
    ];
  }

  const changedRegions: Array<{
    x: number;
    y: number;
    width: number;
    height: number;
    imageData: string;
  }> = [];
  const threshold = 30; // Minimum region size
  const step = 32; // Step size for region detection

  // Simple region detection - check for differences in blocks
  for (let y = 0; y < currentData.height; y += step) {
    for (let x = 0; x < currentData.width; x += step) {
      let hasChanges = false;

      // Check if this block has changes
      for (let dy = 0; dy < step && y + dy < currentData.height; dy++) {
        for (let dx = 0; dx < step && x + dx < currentData.width; dx++) {
          const idx = ((y + dy) * currentData.width + (x + dx)) * 4;
          const prevIdx = ((y + dy) * previousData.width + (x + dx)) * 4;

          if (
            currentData.data[idx] !== previousData.data[idx] ||
            currentData.data[idx + 1] !== previousData.data[idx + 1] ||
            currentData.data[idx + 2] !== previousData.data[idx + 2] ||
            currentData.data[idx + 3] !== previousData.data[idx + 3]
          ) {
            hasChanges = true;
            break;
          }
        }
        if (hasChanges) break;
      }

      if (hasChanges) {
        // Create a region for this block
        const regionWidth = Math.min(step, currentData.width - x);
        const regionHeight = Math.min(step, currentData.height - y);

        // Create a temporary canvas to extract this region
        const tempCanvas = document.createElement("canvas");
        tempCanvas.width = regionWidth;
        tempCanvas.height = regionHeight;
        const tempCtx = tempCanvas.getContext("2d")!;

        // Draw the region from the main canvas
        tempCtx.drawImage(
          canvasRef.value!,
          x,
          y,
          regionWidth,
          regionHeight,
          0,
          0,
          regionWidth,
          regionHeight
        );

        changedRegions.push({
          x,
          y,
          width: regionWidth,
          height: regionHeight,
          imageData: tempCanvas.toDataURL("image/png"),
        });
      }
    }
  }

  return changedRegions;
};

const sendRegionsToServer = async (): Promise<void> => {
  try {
    if (!canvasRef.value || !pixiApp.value) return;

    // Render the current state
    pixiApp.value.render();

    // Get current canvas data
    const ctx = canvasRef.value.getContext("2d")!;
    const currentData = ctx.getImageData(
      0,
      0,
      canvasRef.value.width,
      canvasRef.value.height
    );

    // Detect changed regions
    const detectedRegions = detectChangedRegions(
      currentData,
      previousCanvasData
    );
    regions.value = detectedRegions;

    if (detectedRegions.length === 0) {
      console.log("No changes detected");
      return;
    }

    console.log(`Sending ${detectedRegions.length} regions to server`);

    // Send regions to server
    const response = await fetch(`${serverUrl.value}/update-regions`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        regions: detectedRegions.map((region) => ({
          x: region.x,
          y: region.y,
          width: region.width,
          height: region.height,
          image_data: region.imageData,
        })),
      }),
    });

    if (response.ok) {
      const result = await response.json();
      console.log("Regions sent successfully:", result);
      lastUpdateTime.value = new Date().toLocaleTimeString();

      // Store current data as previous for next comparison
      previousCanvasData = currentData;
    } else {
      console.error("Failed to send regions:", response.statusText);
    }
  } catch (error) {
    console.error("Error sending regions to server:", error);
  }
};

const sendFullImage = async (): Promise<void> => {
  try {
    if (!canvasRef.value || !pixiApp.value) return;
    pixiApp.value.render();
    const base64Image = canvasRef.value.toDataURL("image/png");
    debugImage.value = base64Image;

    await fetch(`${serverUrl.value}/update-display`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ image_data: base64Image }),
    });

    lastUpdateTime.value = new Date().toLocaleTimeString();
  } catch (error) {
    console.error("Error sending to server:", error);
  }
};

const changeText = (): void => {
  const randomWord = Math.random().toString(36).substring(2, 6);
  textToDisplay.value = "Hello PixiJS! " + randomWord;
  textRef!.text = textToDisplay.value;
};

onMounted(async () => {
  if (!canvasRef.value) return;
  const app = new Application();
  await app.init({
    resizeTo: canvasRef.value,
    canvas: canvasRef.value,
    background: "#ffffff",
  });

  pixiApp.value = app;

  textRef = new Text({
    text: textToDisplay.value,
    style: {
      fill: "#000000",
      fontSize: 36,
    },
    anchor: 0.5,
    x: 400,
    y: 240,
  });

  app.stage.addChild(textRef);
  console.log("Text added to stage");
});
</script>

<style scoped>
.app {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f0f0f0;
  padding: 20px;
}

.canvas-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

canvas {
  border: 2px solid #333;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  width: 800px;
  height: 480px;
}

.debug-image {
  border: 2px solid #ff6b6b;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(255, 107, 107, 0.3);
  width: 400px;
  height: 240px;
  object-fit: contain;
  background: #f8f9fa;
}

.controls {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: center;
}

.btn {
  padding: 10px 20px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.2s;
}

.btn:hover {
  background: #0056b3;
}

.debug-info {
  background: #f8f9fa;
  padding: 10px;
  border-radius: 4px;
  border: 1px solid #dee2e6;
  text-align: center;
}

.debug-info p {
  margin: 5px 0;
  font-size: 14px;
  color: #666;
}
</style>
