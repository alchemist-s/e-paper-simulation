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
        self.main_label = None
        self.other_label = None
        self.main_image_tk = None
        self.other_image_tk = None
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
        self.root.title("e-Paper Simulation (Real-Time)")

        # Create labels for main and other images
        self.main_label = tk.Label(self.root, text="Main Display", compound="top")
        self.main_label.grid(row=0, column=0, padx=10, pady=10)

        self.other_label = tk.Label(self.root, text="Other Display", compound="top")
        self.other_label.grid(row=0, column=1, padx=10, pady=10)

    def pil_to_tk(self, img: Image.Image):
        """Convert PIL image to Tkinter PhotoImage"""
        if not TKINTER_AVAILABLE:
            return None

        # Resize for better viewing and convert to RGB for Tkinter
        resized = img.resize((self._width // 2, self._height // 2))
        if img.mode == "1":  # Convert binary to RGB
            resized = resized.convert("RGB")
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
        """Display images in Tkinter window or save to files"""
        if TKINTER_AVAILABLE and self.root:
            # Update main image
            self.main_image_tk = self.pil_to_tk(main_image)
            self.main_label.config(image=self.main_image_tk)
            self.main_label.image = self.main_image_tk

            # Update other image if provided
            if other_image:
                self.other_image_tk = self.pil_to_tk(other_image)
                self.other_label.config(image=self.other_image_tk)
                self.other_label.image = self.other_image_tk

            # Update the window
            self.root.update()
        else:
            # Fallback: save images to files
            self.save_image(main_image, "main")
            if other_image:
                self.save_image(other_image, "other")

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
