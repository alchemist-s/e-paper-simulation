#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
from contextlib import asynccontextmanager
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

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Waveshare EPD imports
try:
    import sys

    # Add the lib directory to Python path
    lib_path = os.path.join(os.path.dirname(__file__), "lib")
    sys.path.append(lib_path)
    logger.info(f"Added lib path: {lib_path}")

    # Import directly from the file since __init__.py is empty
    logger.info("Attempting to import EPD...")
    from waveshare_epd.epd7in5b_V2 import EPD

    logger.info("EPD imported successfully")

    EPD_AVAILABLE = True
except ImportError as e:
    EPD_AVAILABLE = False
    logger.error(f"Waveshare EPD library not available: {e}")
except RuntimeError as e:
    # GPIO error
    EPD_AVAILABLE = False
    logger.error(f"GPIO error: {e}")
except Exception as e:
    EPD_AVAILABLE = False
    logger.error(f"Unexpected error importing EPD: {e}")
    import traceback

    logger.error(f"Traceback: {traceback.format_exc()}")

OUTPUT_DIR = "pixi_images"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# E-Paper display state
epd = None
previous_image = None
is_initialized = False

# E-Paper display dimensions (for epd7in5b_V2)
EPD_WIDTH = 800
EPD_HEIGHT = 480


class PixiImageRequest(BaseModel):
    image: str  # Base64 encoded PNG image


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Initialize e-paper display on app startup"""
    global epd, is_initialized
    logger.info("=== Starting up Pixi server... ===")
    logger.info("Lifespan function called")

    logger.info("Calling init_epd()...")
    if await init_epd():
        logger.info("=== E-paper display initialized successfully on startup ===")
    else:
        logger.warning("=== Failed to initialize e-paper display on startup ===")

    yield

    logger.info("=== Shutting down Pixi server... ===")
    if epd:
        logger.info("Putting EPD to sleep...")
        epd.sleep()


app = FastAPI(title="Pixi Image Receiver", lifespan=lifespan)

# Add CORS middleware to allow Vue app to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def init_epd():
    """Initialize the e-paper display"""
    global epd, is_initialized

    logger.info(f"EPD_AVAILABLE: {EPD_AVAILABLE}")

    if not EPD_AVAILABLE:
        logger.error("EPD library not available")
        return False

    try:
        logger.info("Attempting to initialize real e-paper hardware...")
        logger.info("Creating EPD instance...")
        epd = EPD()
        logger.info("EPD instance created successfully")

        # Initialize for partial updates
        logger.info("Initializing for partial updates...")
        result = epd.init_part()
        logger.info(f"init_part() returned: {result}")

        if result != 0:
            logger.error(
                f"Failed to initialize e-paper display, init_part() returned {result}"
            )
            return False

        logger.info("Clearing display...")
        epd.Clear()
        is_initialized = True
        logger.info("Real e-paper display initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize e-paper display: {e}")
        import traceback

        logger.error(f"Traceback: {traceback.format_exc()}")
        return False


def prepare_image_for_epd(image):
    """Convert image to e-paper format (black and white, correct dimensions)"""
    logger.info(f"Original image size: {image.size}, mode: {image.mode}")

    # Resize to e-paper dimensions
    image = image.resize((EPD_WIDTH, EPD_HEIGHT), Image.Resampling.LANCZOS)
    logger.info(f"Resized image size: {image.size}")

    # Convert to 1-bit (black and white)
    if image.mode != "1":
        image = image.convert("1")

    logger.info(f"Final image size: {image.size}, mode: {image.mode}")

    # Save debug image
    debug_filename = (
        f"debug_epd_image_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.png"
    )
    debug_filepath = os.path.join(OUTPUT_DIR, debug_filename)
    image.save(debug_filepath)
    logger.info(f"Saved debug image: {debug_filename}")

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


async def update_epd_partial(image, regions):
    """Update specific regions of the e-paper display"""
    global epd

    if not epd or not is_initialized:
        logger.error("E-paper display not initialized")
        return False

    try:
        # Update each changed region
        for x_min, y_min, x_max, y_max in regions:
            # Align region boundaries to 8-byte boundaries for e-paper
            if (
                (x_min % 8 + x_max % 8 == 8 and x_min % 8 > x_max % 8)
                or x_min % 8 + x_max % 8 == 0
                or (x_max - x_min) % 8 == 0
            ):
                x_min = x_min // 8 * 8
                x_max = x_max // 8 * 8
            else:
                x_min = x_min // 8 * 8
                if x_max % 8 == 0:
                    x_max = x_max // 8 * 8
                else:
                    x_max = x_max // 8 * 8 + 1

            # Crop the region from the full image
            region_image = image.crop((x_min, y_min, x_max, y_max))

            # Use the EPD's getbuffer method instead of manual buffer creation
            buffer = epd.getbuffer(region_image)

            # Update the region
            epd.display_Partial(buffer, x_min, y_min, x_max, y_max)
            logger.info(f"Updated region: ({x_min},{y_min}) to ({x_max},{y_max})")

        return True
    except Exception as e:
        logger.error(f"Failed to update e-paper display: {e}")
        return False


async def display_first_image(epd_image):
    """Display the first image on e-paper"""
    global epd, previous_image

    logger.info("Creating buffer for first display...")
    buffer = epd.getbuffer(epd_image)
    red_buffer = [0x00] * (int(EPD_WIDTH / 8) * EPD_HEIGHT)
    logger.info(f"Buffer size: {len(buffer)}, Red buffer size: {len(red_buffer)}")
    logger.info("Sending to e-paper display...")
    epd.display(buffer, red_buffer)
    previous_image = epd_image.copy()
    logger.info("First image displayed on e-paper")


@app.post("/")
async def receive_pixi_image(request: PixiImageRequest):
    global previous_image, is_initialized

    try:
        logger.info(f"Received image request. EPD initialized: {is_initialized}")

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

        # Display on e-paper (first image or updates)
        if not is_initialized:
            logger.error("E-paper display not initialized")
            return {
                "status": "error",
                "message": "E-paper display not initialized",
                "filename": filename,
            }
        elif previous_image is None:
            # First image display
            logger.info("First image - using full display update")
            await display_first_image(epd_image)
        else:
            # Detect changed regions and update partially
            logger.info("Subsequent image - detecting changed regions")
            changed_regions = detect_changed_regions(epd_image, previous_image)

            if changed_regions:
                logger.info(
                    f"Found {len(changed_regions)} changed regions, updating display"
                )
                await update_epd_partial(epd_image, changed_regions)
                previous_image = epd_image.copy()
                logger.info(f"Updated {len(changed_regions)} regions on e-paper")
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
        "epd_type": "Real EPD",
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
