#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
import io
import base64
import logging
import numpy as np
import subprocess
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
    # Import directly from the file since __init__.py is empty
    from waveshare_epd.epd7in5b_V2 import EPD

    EPD_AVAILABLE = True
    MOCK_MODE = False
except ImportError as e:
    EPD_AVAILABLE = False
    MOCK_MODE = True
    logging.warning(f"Waveshare EPD library not available: {e}")
except RuntimeError as e:
    # GPIO error - run in mock mode
    EPD_AVAILABLE = False
    MOCK_MODE = True
    logging.warning(f"GPIO error, running in mock mode: {e}")

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

# E-Paper display dimensions (for epd7in5b_V2)
EPD_WIDTH = 800
EPD_HEIGHT = 480


# Mock EPD class for testing without hardware
class MockEPD:
    def __init__(self):
        self.width = 800
        self.height = 480
        self.partFlag = 1

    def init_part(self):
        logging.info("Mock EPD: Initialized for partial updates")
        return 0

    def Clear(self):
        logging.info("Mock EPD: Display cleared")

    def getbuffer(self, image):
        logging.info("Mock EPD: Got buffer for image")
        return [0x00] * (int(self.width / 8) * self.height)

    def display(self, buffer, red_buffer):
        logging.info("Mock EPD: Full display updated")

    def display_Partial(self, buffer, x_min, y_min, x_max, y_max):
        logging.info(
            f"Mock EPD: Partial update at ({x_min},{y_min}) to ({x_max},{y_max})"
        )

    def sleep(self):
        logging.info("Mock EPD: Display sleeping")


class PixiImageRequest(BaseModel):
    image: str  # Base64 encoded PNG image


def init_epd():
    """Initialize the e-paper display"""
    global epd, is_initialized

    logger.info(f"=== INITIALIZING EPD ===")
    logger.info(f"MOCK_MODE: {MOCK_MODE}")
    logger.info(f"EPD_AVAILABLE: {EPD_AVAILABLE}")

    if MOCK_MODE:
        logger.info("Running in mock mode - no actual hardware")
        epd = MockEPD()
        is_initialized = True
        return True

    if not EPD_AVAILABLE:
        logger.error("EPD library not available")
        return False

    try:
        logger.info("Attempting to initialize real e-paper hardware...")
        epd = EPD()
        logger.info(f"EPD object created: {epd}")

        # Initialize for partial updates
        logger.info("Calling epd.init_part()...")
        result = epd.init_part()
        logger.info(f"init_part() returned: {result}")

        if result != 0:
            logger.error("Failed to initialize e-paper display")
            return False

        logger.info("Calling epd.Clear()...")
        epd.Clear()
        logger.info("Clear() completed")

        is_initialized = True
        logger.info("Real e-paper display initialized successfully")
        logger.info("=== EPD INITIALIZATION COMPLETED ===")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize e-paper display: {e}")
        import traceback

        traceback.print_exc()
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


def update_epd_partial(image, regions):
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

            # Convert to buffer
            img = region_image.convert("1")
            buf = bytearray(img.tobytes("raw"))

            # Invert the bytes (same as getbuffer does)
            for i in range(len(buf)):
                buf[i] ^= 0xFF

            # Update the region
            epd.display_Partial(buf, x_min, y_min, x_max, y_max)
            logger.info(f"Updated region: ({x_min},{y_min}) to ({x_max},{y_max})")

        return True
    except Exception as e:
        logger.error(f"Failed to update e-paper display: {e}")
        return False


def display_first_image(epd_image):
    """Display the first image on e-paper"""
    global epd, previous_image

    logger.info("=== STARTING FIRST DISPLAY ===")
    logger.info(f"EPD object: {epd}")
    logger.info(f"EPD type: {type(epd)}")

    logger.info("Creating buffer for first display...")
    buffer = epd.getbuffer(epd_image)
    red_buffer = [0x00] * (int(EPD_WIDTH / 8) * EPD_HEIGHT)
    logger.info(f"Buffer size: {len(buffer)}, Red buffer size: {len(red_buffer)}")

    logger.info("Sending to e-paper display...")
    try:
        epd.display(buffer, red_buffer)
        logger.info("Display command completed successfully")
    except Exception as e:
        logger.error(f"Display command failed: {e}")
        raise

    previous_image = epd_image.copy()
    logger.info("=== FIRST DISPLAY COMPLETED ===")


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

        # Run EPD test with the latest image
        logger.info("Running EPD test with latest image...")
        success = run_epd_test_with_latest_image()

        if success:
            logger.info("EPD test completed successfully")
        else:
            logger.error("EPD test failed")

        return {
            "status": "success",
            "filename": filename,
            "epd_updated": success,
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


def run_epd_test_with_latest_image():
    """Run the test script with the latest saved image"""
    try:
        # Find the latest image
        pixi_images = [
            f
            for f in os.listdir(OUTPUT_DIR)
            if f.startswith("pixi_") and f.endswith(".png")
        ]
        if not pixi_images:
            logger.error("No PixiJS images found to test")
            return False

        latest_image = sorted(pixi_images)[-1]
        logger.info(f"Running EPD test with latest image: {latest_image}")

        # Run the test script
        script_path = os.path.join(os.path.dirname(__file__), "test_existing_image.py")
        result = subprocess.run(
            ["python3", script_path],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(__file__),
        )

        logger.info(f"Test script stdout: {result.stdout}")
        if result.stderr:
            logger.warning(f"Test script stderr: {result.stderr}")

        logger.info(f"Test script completed with return code: {result.returncode}")
        return result.returncode == 0

    except Exception as e:
        logger.error(f"Failed to run EPD test: {e}")
        return False


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
