#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
import io
import base64
import logging
import numpy as np
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image
import uvicorn
import subprocess
import asyncio

# Import the EPD queue processor
from epd_queue_processor import get_epd_processor

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OUTPUT_DIR = "pixi_images"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Track the previous image filename
previous_image_filename = None


class PixiImageRequest(BaseModel):
    image: str  # Base64 encoded PNG image


app = FastAPI(title="Pixi E-Paper Server", version="1.0.0")

# Add CORS middleware to allow Vue app to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def clear_pixi_images_directory():
    """Clear all files from the pixi_images directory"""
    try:
        logger.info("Clearing pixi_images directory...")
        for filename in os.listdir(OUTPUT_DIR):
            file_path = os.path.join(OUTPUT_DIR, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                logger.info(f"Removed: {filename}")
        logger.info("pixi_images directory cleared")
    except Exception as e:
        logger.error(f"Error clearing pixi_images directory: {e}")


@app.on_event("startup")
async def startup_event():
    """Initialize on app startup"""
    global previous_image_filename

    logger.info("=== Starting up Pixi server... ===")
    logger.info("Server ready to receive images")

    # Clear the pixi_images directory
    clear_pixi_images_directory()

    # Start the EPD queue processor
    try:
        epd_processor = await get_epd_processor()
        await epd_processor.start()
        logger.info("EPD queue processor started successfully")
    except Exception as e:
        logger.error(f"Error starting EPD queue processor: {e}")

    # Initialize the EPD display
    try:
        logger.info("Initializing EPD display...")
        result = subprocess.run(
            ["sudo", "python3", "epd_init.py"],
            capture_output=True,
            text=True,
            cwd=os.getcwd(),
        )

        if result.returncode == 0:
            logger.info("EPD display initialized successfully")
            logger.info(f"EPD init output: {result.stdout}")
        else:
            logger.error(
                f"EPD initialization failed with return code {result.returncode}"
            )
            logger.error(f"EPD init stderr: {result.stderr}")

    except Exception as e:
        logger.error(f"Error initializing EPD display: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on app shutdown"""
    logger.info("=== Shutting down Pixi server... ===")

    # Stop the EPD queue processor
    try:
        epd_processor = await get_epd_processor()
        await epd_processor.stop()
        logger.info("EPD queue processor stopped")
    except Exception as e:
        logger.error(f"Error stopping EPD queue processor: {e}")

    # Clear the pixi_images directory
    clear_pixi_images_directory()

    # Put EPD display to sleep
    try:
        logger.info("Putting EPD display to sleep...")
        result = subprocess.run(
            ["sudo", "python3", "epd_sleep.py"],
            capture_output=True,
            text=True,
            cwd=os.getcwd(),
        )

        if result.returncode == 0:
            logger.info("EPD display put to sleep successfully")
        else:
            logger.error(f"Failed to put EPD to sleep: {result.stderr}")

    except Exception as e:
        logger.error(f"Error putting EPD to sleep: {e}")


@app.post("/")
async def receive_pixi_image(request: PixiImageRequest):
    global previous_image_filename

    try:
        logger.info("Received image request")

        # Decode base64 image data
        image_data = request.image
        if "," in image_data:
            image_data = image_data.split(",", 1)[1]
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))

        # Save image with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"pixi_{timestamp}.png"
        filepath = os.path.join(OUTPUT_DIR, filename)
        image.save(filepath)
        logger.info(f"Saved Pixi image: {filename}")

        # Add the image update to the EPD queue
        try:
            epd_processor = await get_epd_processor()
            success = await epd_processor.add_update(filepath)

            if success:
                logger.info(f"Added image to EPD queue: {filename}")
                # Update the previous image filename
                previous_image_filename = filename
                epd_updated = True
            else:
                logger.error(f"Failed to add image to EPD queue: {filename}")
                epd_updated = False

        except Exception as e:
            logger.error(f"Error adding image to EPD queue: {e}")
            epd_updated = False

        # Return success response
        return {
            "status": "success",
            "message": f"Image {filename} received and queued for EPD update",
            "epd_updated": epd_updated,
            "filename": filename,
        }

    except Exception as e:
        logger.error(f"Error processing image request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
async def get_status():
    """Get the current status of the EPD queue processor"""
    try:
        epd_processor = await get_epd_processor()
        status = await epd_processor.get_queue_status()
        return {
            "status": "success",
            "epd_queue": status,
            "previous_image": previous_image_filename,
        }
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
