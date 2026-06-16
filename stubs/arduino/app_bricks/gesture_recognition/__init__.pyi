import numpy as np
from _typeshed import Incomplete
from arduino.app_internal.core.module import load_brick_compose_file as load_brick_compose_file, resolve_address as resolve_address
from arduino.app_peripherals.camera import BaseCamera as BaseCamera, Camera as Camera
from arduino.app_utils import Logger as Logger, brick as brick
from arduino.app_utils.image.adjustments import compress_to_jpeg as compress_to_jpeg
from typing import Callable, Literal

logger: Incomplete

class GestureRecognition:
    def __init__(self, camera: BaseCamera | None = None, confidence: float = 0.0) -> None: ...
    def start(self) -> None:
        """Start the capture thread and asyncio event loop."""
    def stop(self) -> None:
        """Stop all tracking and close connections."""
    def on_gesture(self, gesture: str, callback: Callable[[dict], None], hand: Literal['left', 'right', 'both'] = 'both'):
        '''
        Register or unregister a gesture callback.

        Args:
            gesture (str): The gesture name to detect
            callback (Callable[[dict], None]): Function to call when gesture is detected. None to unregister.
                The callback receives a metadata dictionary with details about the detection, including:
                - "hand": Which hand performed the gesture ("left" or "right")
                - "gesture": Name of the detected gesture
                - "confidence": Confidence score of the detection (0.0 to 1.0)
                - "landmarks": List of key points of the detected hand (in (x, y, z) format where
                    x and y are pixel coordinates and z is normalized depth)
                - "bounding_box_xyxy": [x_min, y_min, x_max, y_max] of the detected hand bounding box
            hand (Literal["left", "right", "both"]): Which hand(s) to track

        Raises:
            ValueError: If \'hand\' argument is not valid
        '''
    def on_enter(self, callback: Callable[[], None]):
        """
        Register a callback for when hands become visible.

        Args:
            callback (Callable[[], None]): Function to call when at least one hand is detected
        """
    def on_exit(self, callback: Callable[[], None]):
        """
        Register a callback for when hands are no longer visible.

        Args:
            callback (Callable[[], None]): Function to call when no hands are detected anymore
        """
    def on_frame(self, callback: Callable[[np.ndarray], None]):
        """
        Register a callback that receives each camera frame.

        Args:
            callback (Callable[[np.ndarray], None]): Function to call with camera frame data. None to unregister.
        """
