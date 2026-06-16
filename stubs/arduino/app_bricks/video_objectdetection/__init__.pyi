from _typeshed import Incomplete
from arduino.app_internal.core import EdgeImpulseRunnerFacade as EdgeImpulseRunnerFacade, load_brick_compose_file as load_brick_compose_file, resolve_address as resolve_address
from arduino.app_peripherals.camera import BaseCamera as BaseCamera, Camera as Camera
from arduino.app_utils import Logger as Logger, brick as brick
from arduino.app_utils.image.adjustments import compress_to_jpeg as compress_to_jpeg
from typing import Callable
from websockets.sync.connection import Connection as Connection

logger: Incomplete

class VideoObjectDetection:
    """Module for object detection on a **live video stream** using a specified machine learning model.

    This brick:
      - Connects to a model runner over WebSocket.
      - Parses incoming classification messages with bounding boxes.
      - Filters detections by a configurable confidence threshold.
      - Debounces repeated triggers of the same label.
      - Invokes per-label callbacks and/or a catch-all callback.
    """
    ALL_HANDLERS_KEY: str
    def __init__(self, camera: BaseCamera | None = None, confidence: float = 0.3, debounce_sec: float = 0.0, camera_preview: bool = False) -> None:
        """Initialize the VideoObjectDetection class.

        Args:
            camera (BaseCamera): The camera instance to use for capturing video. If None, a default camera will be initialized.
            confidence (float): Confidence level for detection. Default is 0.3 (30%).
            debounce_sec (float): Minimum seconds between repeated detections of the same object. Default is 0 seconds.
            camera_preview (bool): Receive current camera frame on callback invocation.
                Frame is a raw jpeg-encoded image without bounding boxes applied on it. Default is False.

        Raises:
            RuntimeError: If the host address could not be resolved.
        """
    def on_detect(self, object: str, callback: Callable[[], None]):
        """Register a callback invoked when a **specific label** is detected.

        Args:
            object (str): The label of the object to check for in the classification results.
            callback (Callable[[], None]): A function with **no parameters**.

        Raises:
            TypeError: If `callback` is not a function.
            ValueError: If `callback` accepts any parameters.
        """
    def on_detect_all(self, callback: Callable[[dict], None]):
        """Register a callback invoked for **every detection event**.

        This is useful to receive a consolidated dictionary of detections for each frame.

        Args:
            callback (Callable[[dict], None]): A function that accepts **one dict argument** with
                the shape `{label: confidence, ...}`.

        Raises:
            TypeError: If `callback` is not a function.
            ValueError: If `callback` does not accept exactly one argument.
        """
    def start(self) -> None:
        """Start the video object detection process."""
    def stop(self) -> None:
        """Stop the video object detection process and release resources."""
    @brick.execute
    def object_detection_loop(self) -> None:
        """Object detection main loop.

        Maintains WebSocket connection to the model runner and processes object detection messages.
        Retries on connection errors until stopped.
        """
    @brick.execute
    def camera_loop(self) -> None:
        """Camera main loop.

        Captures images from the camera and forwards them over the TCP connection.
        Retries on connection errors until stopped.
        """
    def override_threshold(self, value: float):
        """Override the threshold for object detection model.

        Args:
            value (float): The new value for the threshold in the range [0.0, 1.0].

        Raises:
            TypeError: If the value is not a number.
            RuntimeError: If the model information is not available or does not support threshold override.
        """
