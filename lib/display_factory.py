from display_interface import DisplayInterface
from hardware_display import HardwareDisplay


class DisplayFactory:
    """Factory for creating display implementations"""

    @staticmethod
    def create_display(
        simulate: bool, epd_module=None, width=800, height=480
    ) -> DisplayInterface:
        """
        Create a display implementation based on simulation flag

        Args:
            simulate: If True, use simulation display
            epd_module: The e-paper module (required for hardware mode)
            width: Display width (used for simulation)
            height: Display height (used for simulation)

        Returns:
            DisplayInterface implementation
        """
        if simulate:
            # Only import SimulationDisplay when simulation is requested
            from simulation_display import SimulationDisplay

            return SimulationDisplay(width=width, height=height)
        else:
            if epd_module is None:
                raise ValueError("epd_module is required for hardware mode")
            return HardwareDisplay(epd_module)
