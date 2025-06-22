#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import asyncio
import subprocess
import logging
import os
from datetime import datetime
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EPDQueueProcessor:
    def __init__(self):
        """Initialize the EPD queue processor"""
        self.queue = asyncio.Queue()
        self.processing = False
        self.current_task: Optional[asyncio.Task] = None
        self.previous_image_filename: Optional[str] = None

    async def start(self):
        """Start the queue processor"""
        logger.info("Starting EPD queue processor...")
        self.processing = True
        self.current_task = asyncio.create_task(self._process_queue())
        logger.info("EPD queue processor started")

    async def stop(self):
        """Stop the queue processor"""
        logger.info("Stopping EPD queue processor...")
        self.processing = False
        if self.current_task:
            self.current_task.cancel()
            try:
                await self.current_task
            except asyncio.CancelledError:
                pass
        logger.info("EPD queue processor stopped")

    async def add_update(self, image_filepath: str) -> bool:
        """Add an image update to the queue"""
        try:
            await self.queue.put(image_filepath)
            logger.info(f"Added image update to queue: {image_filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to add image to queue: {e}")
            return False

    async def _process_queue(self):
        """Process the queue of image updates"""
        while self.processing:
            try:
                # Wait for an item in the queue
                image_filepath = await asyncio.wait_for(self.queue.get(), timeout=1.0)

                logger.info(f"Processing image update: {image_filepath}")

                # Process the image update
                success = await self._update_epd_display(image_filepath)

                if success:
                    # Update the previous image filename for next update
                    self.previous_image_filename = os.path.basename(image_filepath)
                    logger.info(f"EPD update completed successfully: {image_filepath}")
                else:
                    logger.error(f"EPD update failed: {image_filepath}")

                # Mark the task as done
                self.queue.task_done()

            except asyncio.TimeoutError:
                # No items in queue, continue waiting
                continue
            except asyncio.CancelledError:
                logger.info("Queue processor cancelled")
                break
            except Exception as e:
                logger.error(f"Error in queue processor: {e}")
                continue

    async def _update_epd_display(self, image_filepath: str) -> bool:
        """Update the EPD display with the given image"""
        try:
            # Build the command
            cmd = ["python3", "epd_updater.py", image_filepath]
            if self.previous_image_filename:
                previous_filepath = os.path.join(
                    "pixi_images", self.previous_image_filename
                )
                if os.path.exists(previous_filepath):
                    cmd.append(previous_filepath)
                    logger.info(f"Using previous image: {self.previous_image_filename}")
                else:
                    logger.warning(f"Previous image not found: {previous_filepath}")

            logger.info(f"Running EPD updater command: {' '.join(cmd)}")

            # Run the subprocess asynchronously
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=os.getcwd(),
            )

            # Wait for the process to complete
            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                logger.info("EPD updater completed successfully")
                if stdout:
                    logger.info(f"EPD updater output: {stdout.decode()}")
                return True
            else:
                logger.error(
                    f"EPD updater failed with return code {process.returncode}"
                )
                if stderr:
                    logger.error(f"EPD updater stderr: {stderr.decode()}")
                return False

        except Exception as e:
            logger.error(f"Error updating EPD display: {e}")
            return False

    async def get_queue_status(self) -> dict:
        """Get the current status of the queue"""
        return {
            "queue_size": self.queue.qsize(),
            "processing": self.processing,
            "previous_image": self.previous_image_filename,
        }


# Global instance
epd_processor = EPDQueueProcessor()


async def get_epd_processor() -> EPDQueueProcessor:
    """Get the global EPD processor instance"""
    return epd_processor
