from _typeshed import Incomplete
from arduino.app_internal.core import EdgeImpulseRunnerFacade as EdgeImpulseRunnerFacade
from arduino.app_utils import Logger as Logger, SlidingWindowBuffer as SlidingWindowBuffer, brick as brick
from typing import Iterable

logger: Incomplete

class MotionDetection(EdgeImpulseRunnerFacade):
    """This Motion Detection module classifies motion patterns using accelerometer data."""
    def __init__(self, confidence: float = 0.4) -> None:
        """Initialize the MotionDetection module.

        Args:
            confidence (float): Confidence level for detection. Default is 0.4 (40%).
        """
    def start(self) -> None: ...
    def stop(self) -> None: ...
    def on_movement_detection(self, movement: str, callback: callable):
        """Register a callback function to be invoked when a specific motion pattern is detected.

        Args:
            movement (str): The motion pattern name to check for in the classification results.
            callback (callable): Function to call when the specified motion pattern is detected.
        """
    def accumulate_samples(self, accelerometer_samples: tuple[float, float, float]):
        """Accumulate accelerometer samples for motion detection.

        Args:
            accelerometer_samples (tuple): A tuple containing x, y, z acceleration values. Typically, these values are
                in m/s^2, but depends on the model configuration.
        """
    def get_sensor_samples(self) -> Iterable[tuple[float, float, float]]:
        """Get the current sensor samples.

        Returns:
            iterable: An iterable containing the accumulated sensor data (x, y, z acceleration values).
        """
