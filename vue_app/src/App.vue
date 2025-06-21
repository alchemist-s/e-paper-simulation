<template>
  <div class="app">
    <div class="canvas-container">
      <!-- PixiJS Canvas -->
      <canvas ref="canvasRef"></canvas>
      <!-- Controls -->
      <div class="controls">
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

const sendToServer = async (): Promise<void> => {
  try {
    if (!pixiApp.value) return;
    const base64Image = await pixiApp.value.renderer.extract.base64({
      target: pixiApp.value.stage as Container,
      clearColor: "#000000",
      antialias: true,
    });

    const response = await fetch(serverUrl.value, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ image: base64Image }),
    });
    console.log(response);
  } catch (error) {
    console.error("Error sending to server:", error);
  }
};

onMounted(async () => {
  if (!canvasRef.value) return;

  const app = new Application();
  await app.init({
    resizeTo: canvasRef.value,
    canvas: canvasRef.value,
  });

  pixiApp.value = app;

  const myText = new Text({
    text: "Hello MAMA!",
    style: {
      fill: "#ffffff",
      fontSize: 36,
    },
    anchor: 0.5,
    x: 400,
    y: 240,
  });

  app.stage.addChild(myText);
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
