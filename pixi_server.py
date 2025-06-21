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

# Waveshare EPD imports
try:
    import sys

    # Add the lib directory to Python path
    lib_path = os.path.join(os.path.dirname(__file__), "lib")
    sys.path.append(lib_path)
    from waveshare_epd import epd2in13_V4

    EPD_AVAILABLE = True
except ImportError:
    EPD_AVAILABLE = False
    logging.warning(
        "Waveshare EPD library not available. Install with: pip install waveshare-epd"
    )

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Pixi Image Receiver")

# Add CORS middleware to allow Vue app to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OUTPUT_DIR = "pixi_images"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# E-Paper display state
epd = None
previous_image = None
is_initialized = False

# E-Paper display dimensions (for epd2in13_V4)
EPD_WIDTH = 212
EPD_HEIGHT = 104


class PixiImageRequest(BaseModel):
    image: str  # Base64 encoded PNG image


def init_epd():
    """Initialize the e-paper display"""
    global epd, is_initialized

    if not EPD_AVAILABLE:
        logger.error("EPD library not available")
        return False

    try:
        epd = epd2in13_V4.EPD()
        epd.init()
        epd.Clear()
        is_initialized = True
        logger.info("E-paper display initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize e-paper display: {e}")
        return False


def prepare_image_for_epd(image):
    """Convert image to e-paper format (black and white, correct dimensions)"""
    # Resize to e-paper dimensions
    image = image.resize((EPD_WIDTH, EPD_HEIGHT), Image.Resampling.LANCZOS)

    # Convert to grayscale
    if image.mode != "L":
        image = image.convert("L")

    # Convert to black and white (threshold)
    threshold = 128
    image = image.point(lambda x: 0 if x < threshold else 255, "1")

    return image


def detect_changed_regions(new_image, old_image):
    """Detect regions that have changed between two images"""
    if old_image is None:
        # First image - return full display area
        return [(0, 0, EPD_WIDTH, EPD_HEIGHT)]

    # Ensure both images are the same size and format
    new_array = np.array(new_image)
    old_array = np.array(old_image)

    if new_array.shape != old_array.shape:
        # Size changed - return full area
        return [(0, 0, EPD_WIDTH, EPD_HEIGHT)]

    # Find differences
    diff_array = new_array != old_array

    if not np.any(diff_array):
        # No changes detected
        return []

    # Find connected regions of changes
    regions = find_connected_regions(diff_array)
    return regions


def find_connected_regions(diff_array):
    """Find connected regions of changed pixels"""
    from scipy import ndimage

    # Label connected components
    labeled_array, num_features = ndimage.label(diff_array)

    regions = []
    for i in range(1, num_features + 1):
        # Get coordinates of this region
        coords = np.where(labeled_array == i)
        if len(coords[0]) > 0:
            y_min, y_max = coords[0].min(), coords[0].max()
            x_min, x_max = coords[1].min(), coords[1].max()

            # Add some padding to ensure complete updates
            padding = 2
            x_min = max(0, x_min - padding)
            y_min = max(0, y_min - padding)
            x_max = min(EPD_WIDTH - 1, x_max + padding)
            y_max = min(EPD_HEIGHT - 1, y_max + padding)

            regions.append((x_min, y_min, x_max, y_max))

    return regions


def update_epd_partial(image, regions):
    """Update specific regions of the e-paper display"""
    global epd

    if not epd or not is_initialized:
        logger.error("E-paper display not initialized")
        return False

    try:
        # Convert image to bytes for e-paper
        image_bytes = image.tobytes()

        # Update each changed region
        for x_min, y_min, x_max, y_max in regions:
            width = x_max - x_min + 1
            height = y_max - y_min + 1

            # Extract region data
            region_data = []
            for y in range(y_min, y_max + 1):
                row_start = y * EPD_WIDTH + x_min
                row_end = row_start + width
                region_data.extend(image_bytes[row_start:row_end])

            # Update the region
            epd.display_Partial(region_data, x_min, y_min, width, height)
            logger.info(f"Updated region: ({x_min},{y_min}) to ({x_max},{y_max})")

        return True
    except Exception as e:
        logger.error(f"Failed to update e-paper display: {e}")
        return False


@app.post("/")
async def receive_pixi_image(request: PixiImageRequest):
    global previous_image, is_initialized

    try:
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

        # Prepare image for e-paper display
        epd_image = prepare_image_for_epd(image)

        # Initialize e-paper display on first image
        if not is_initialized:
            if init_epd():
                # First full display
                epd_image_bytes = epd_image.tobytes()
                epd.display(epd_image_bytes)
                previous_image = epd_image.copy()
                logger.info("First image displayed on e-paper")
            else:
                logger.error("Failed to initialize e-paper display")
        else:
            # Detect changed regions and update partially
            changed_regions = detect_changed_regions(epd_image, previous_image)

            if changed_regions:
                if update_epd_partial(epd_image, changed_regions):
                    previous_image = epd_image.copy()
                    logger.info(f"Updated {len(changed_regions)} regions on e-paper")
                else:
                    logger.error("Failed to update e-paper display")
            else:
                logger.info("No changes detected, skipping e-paper update")

        return {
            "status": "success",
            "filename": filename,
            "epd_updated": (
                is_initialized and len(changed_regions) > 0
                if "changed_regions" in locals()
                else False
            ),
            "regions_updated": (
                len(changed_regions) if "changed_regions" in locals() else 0
            ),
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
        "epd_available": EPD_AVAILABLE,
        "is_initialized": is_initialized,
        "display_dimensions": f"{EPD_WIDTH}x{EPD_HEIGHT}",
        "previous_image_exists": previous_image is not None,
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
