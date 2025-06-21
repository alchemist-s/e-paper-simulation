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
        <button @click="sendToServer" class="btn">Send to Server</button>
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
let textRef: Text | null = null;

const sendToServer = async (): Promise<void> => {
  try {
    if (!canvasRef.value || !pixiApp.value) return;

    // Force a render before capturing
    pixiApp.value.render();

    // Use canvas toDataURL instead of Pixi's renderer.extract
    const base64Image = canvasRef.value.toDataURL("image/png");

    // Debug: Check if canvas has content
    console.log(
      "Canvas dimensions:",
      canvasRef.value.width,
      "x",
      canvasRef.value.height
    );
    console.log("Base64 image length:", base64Image.length);
    console.log("Base64 starts with:", base64Image.substring(0, 50));

    // Set debug image
    debugImage.value = base64Image;

    await fetch(serverUrl.value, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ image: base64Image }),
    });
    console.log("Canvas captured successfully");
  } catch (error) {
    console.error("Error sending to server:", error);
  }
};

const changeText = (): void => {
  // add random 4 letter word to the text
  const randomWord = Math.random().toString(36).substring(2, 6);
  textToDisplay.value = "Hello PixiJS! " + randomWord;
  textRef!.text = textToDisplay.value;
};

onMounted(async () => {
  if (!canvasRef.value) return;

  console.log("Initializing PixiJS...");
  console.log("Canvas element:", canvasRef.value);
  console.log(
    "Canvas dimensions before init:",
    canvasRef.value.width,
    "x",
    canvasRef.value.height
  );

  const app = new Application();
  await app.init({
    resizeTo: canvasRef.value,
    canvas: canvasRef.value,
  });

  console.log("PixiJS initialized");
  console.log("App canvas:", app.canvas);
  console.log(
    "Canvas dimensions after init:",
    canvasRef.value.width,
    "x",
    canvasRef.value.height
  );

  pixiApp.value = app;

  textRef = new Text({
    text: textToDisplay.value,
    style: {
      fill: "#ffffff",
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
</style>
