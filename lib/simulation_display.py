import tkinter as tk
from display_interface import DisplayInterface
import time
import os

# Try to import PIL components, with fallback handling
try:
    from PIL import Image, ImageTk

    TKINTER_AVAILABLE = True
except ImportError:
    from PIL import Image

    TKINTER_AVAILABLE = False
    print(
        "Warning: ImageTk not available. Simulation will save images to files instead of displaying them."
    )


class SimulationDisplay(DisplayInterface):
    """Simulation implementation using Tkinter for real-time display"""

    def __init__(self, width=800, height=480):
        self._width = width
        self._height = height
        self.root = None
        self.display_label = None
        self.combined_image_tk = None
        self.image_counter = 0

        # Create output directory for saved images
        self.output_dir = "simulation_output"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        if TKINTER_AVAILABLE:
            self.setup_tkinter()
        else:
            print(
                f"Tkinter not available. Images will be saved to '{self.output_dir}' directory."
            )

    def setup_tkinter(self):
        """Setup Tkinter window and labels"""
        if not TKINTER_AVAILABLE:
            return

        self.root = tk.Tk()
        self.root.title("e-Paper Display Simulation")

        # Configure window with e-paper-like styling
        self.root.configure(bg="#f0f0f0")  # Light gray background

        # Create a frame to hold the display with border
        display_frame = tk.Frame(
            self.root, bg="#2c2c2c", relief="raised", bd=3  # Dark border
        )
        display_frame.pack(padx=30, pady=30)

        # Create a single label for the combined display
        self.display_label = tk.Label(
            display_frame,
            text="e-Paper Display",
            compound="top",
            bg="#f8f8f8",  # Paper-like background
            fg="#333333",  # Dark text
        )
        self.display_label.pack(padx=10, pady=10)

    def combine_images(self, black_image: Image.Image, red_image: Image.Image = None):
        """Combine black and red images into a realistic e-paper display"""
        # Start with the black image as base
        if black_image.mode != "RGB":
            combined = black_image.convert("RGB")
        else:
            combined = black_image.copy()

        # If we have a red image, overlay it
        if red_image is not None:
            # Convert red image to RGB if needed
            if red_image.mode != "RGB":
                red_rgb = red_image.convert("RGB")
            else:
                red_rgb = red_image.copy()

            # Create a mask for red pixels (where red image is black)
            # In e-paper, black pixels in the red image become red
            red_mask = red_image.convert("L")  # Convert to grayscale
            red_pixels = red_mask.point(
                lambda x: 0 if x < 128 else 255
            )  # Threshold to binary

            # Apply red color where the mask is black
            red_data = red_rgb.load()
            combined_data = combined.load()
            mask_data = red_pixels.load()

            for y in range(red_image.height):
                for x in range(red_image.width):
                    if mask_data[x, y] == 0:  # Black pixel in red image
                        # Make it red (RGB: 255, 0, 0)
                        combined_data[x, y] = (255, 0, 0)

        return combined

    def pil_to_tk(self, img: Image.Image):
        """Convert PIL image to Tkinter PhotoImage"""
        if not TKINTER_AVAILABLE:
            return None

        # Resize for better viewing
        resized = img.resize((self._width, self._height))
        return ImageTk.PhotoImage(resized)

    def save_image(self, img: Image.Image, prefix: str):
        """Save image to file as fallback when Tkinter is not available"""
        self.image_counter += 1
        filename = f"{self.output_dir}/{prefix}_{self.image_counter}.png"
        img.save(filename)
        print(f"Saved {prefix} image to: {filename}")

    def init(self):
        """Initialize the display (no-op for simulation)"""
        pass

    def clear(self):
        """Clear the display (no-op for simulation)"""
        pass

    def display(self, main_image: Image.Image, other_image: Image.Image = None):
        """Display combined images in Tkinter window or save to files"""
        if TKINTER_AVAILABLE and self.root:
            # Combine the images into a realistic e-paper display
            combined_image = self.combine_images(main_image, other_image)

            # Convert to Tkinter format and display
            self.combined_image_tk = self.pil_to_tk(combined_image)
            self.display_label.config(image=self.combined_image_tk)
            self.display_label.image = self.combined_image_tk

            # Update the window
            self.root.update()
        else:
            # Fallback: save combined image to file
            combined_image = self.combine_images(main_image, other_image)
            self.save_image(combined_image, "combined")

    def init_fast(self):
        """Initialize for fast mode (no-op for simulation)"""
        pass

    def sleep(self):
        """Put display to sleep (close window for simulation)"""
        if self.root:
            self.root.quit()
            self.root.destroy()

    def run(self):
        """Start the Tkinter main loop"""
        if self.root and TKINTER_AVAILABLE:
            self.root.mainloop()

    @property
    def width(self) -> int:
        """Display width in pixels"""
        return self._width

    @property
    def height(self) -> int:
        """Display height in pixels"""
        return self._height
