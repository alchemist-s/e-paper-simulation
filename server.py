#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import sys
import os
import io
import base64
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image
import uvicorn

# Add the lib directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))

from smart_image_updater import SmartImageUpdater

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="E-Paper Web Display Server")

# Add CORS middleware to allow web app to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ScreenshotRequest(BaseModel):
    image_data: str  # Base64 encoded image


# Initialize the smart image updater
smart_updater = None


@app.on_event("startup")
async def startup_event():
    """Initialize the e-paper display on startup"""
    global smart_updater
    try:
        smart_updater = SmartImageUpdater()
        logger.info("E-paper display initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize e-paper display: {e}")
        # Continue without hardware for development
        smart_updater = None


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up the e-paper display on shutdown"""
    global smart_updater
    if smart_updater:
        try:
            smart_updater.epd.sleep()
            logger.info("E-paper display put to sleep")
        except Exception as e:
            logger.error(f"Error putting display to sleep: {e}")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "running", "display_connected": smart_updater is not None}


@app.post("/update-display")
async def update_display(request: ScreenshotRequest):
    """Update the e-paper display with a new screenshot"""
    global smart_updater

    if not smart_updater:
        raise HTTPException(status_code=503, detail="E-paper display not available")

    try:
        # Decode base64 image data
        image_data = base64.b64decode(
            request.image_data.split(",")[1]
            if "," in request.image_data
            else request.image_data
        )

        # Convert to PIL Image
        image = Image.open(io.BytesIO(image_data))

        # Update the display using our smart updater
        smart_updater.update_image(image)

        logger.info("Display updated successfully")
        return {"status": "success", "message": "Display updated"}

    except Exception as e:
        logger.error(f"Error updating display: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to update display: {str(e)}"
        )


@app.get("/status")
async def get_status():
    """Get current display status"""
    global smart_updater
    return {
        "display_connected": smart_updater is not None,
        "first_update": smart_updater.first_update if smart_updater else None,
        "current_image": (
            "available" if smart_updater and smart_updater.current_image else "none"
        ),
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
