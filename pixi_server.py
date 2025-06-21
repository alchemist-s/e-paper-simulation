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

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OUTPUT_DIR = "pixi_images"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Track the previous image filename
previous_image_filename = None


class PixiImageRequest(BaseModel):
    image: str  # Base64 encoded PNG image


app = FastAPI(title="Pixi Image Receiver")

# Add CORS middleware to allow Vue app to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize on app startup"""
    global previous_image_filename

    logger.info("=== Starting up Pixi server... ===")
    logger.info("Server ready to receive images")

    # Initialize the EPD display
    try:
        logger.info("Initializing EPD display...")
        result = subprocess.run(
            ["python3", "epd_init.py"], capture_output=True, text=True, cwd=os.getcwd()
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

        # Call the EPD updater script
        try:
            cmd = ["python3", "epd_updater.py", filepath]
            if previous_image_filename:
                previous_filepath = os.path.join(OUTPUT_DIR, previous_image_filename)
                cmd.append(previous_filepath)
                logger.info(
                    f"Calling EPD updater with new: {filename}, previous: {previous_image_filename}"
                )
            else:
                logger.info(f"Calling EPD updater with first image: {filename}")

            # Run the subprocess
            result = subprocess.run(
                cmd, capture_output=True, text=True, cwd=os.getcwd()
            )

            if result.returncode == 0:
                logger.info("EPD updater completed successfully")
                logger.info(f"EPD updater output: {result.stdout}")
                epd_updated = True
            else:
                logger.error(f"EPD updater failed with return code {result.returncode}")
                logger.error(f"EPD updater stderr: {result.stderr}")
                epd_updated = False

        except Exception as e:
            logger.error(f"Error calling EPD updater: {e}")
            epd_updated = False

        # Update the previous image filename
        previous_image_filename = filename

        return {
            "status": "success",
            "filename": filename,
            "epd_updated": epd_updated,
            "previous_image": previous_image_filename,
        }

    except Exception as e:
        logger.error(f"Error processing Pixi image: {e}")
        raise HTTPException(
            status_code=400, detail=f"Failed to process image: {str(e)}"
        )


@app.get("/epd-status")
async def get_epd_status():
    """Get e-paper display status"""
    return {
        "status": "running",
        "previous_image": previous_image_filename,
        "output_directory": OUTPUT_DIR,
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
