from _typeshed import Incomplete
from arduino.app_internal.core import EdgeImpulseRunnerFacade as EdgeImpulseRunnerFacade, load_brick_compose_file as load_brick_compose_file, resolve_address as resolve_address
from arduino.app_peripherals.camera import BaseCamera as BaseCamera, Camera as Camera
from arduino.app_utils import Logger as Logger, brick as brick
from arduino.app_utils.image.adjustments import compress_to_jpeg as compress_to_jpeg
from typing import Callable
from websockets.sync.connection import Connection as Connection

logger: Incomplete

class VideoImageClassification:
    """Module for image classification on a **live video stream** using a specified machine learning model.

    Provides a way to react to detected classes over a video stream invoking registered actions in real-time.
    """
    ALL_HANDLERS_KEY: str
    def __init__(self, camera: BaseCamera | None = None, confidence: float = 0.3, debounce_sec: float = 0.0) -> None:
        """Initialize the VideoImageClassification class.

        Args:
            camera (BaseCamera): The camera instance to use for capturing video. If None, a default camera will be initialized.
            confidence (float): The minimum confidence level for a classification to be considered valid. Default is 0.3.
            debounce_sec (float): The minimum time in seconds between consecutive detections of the same object
                to avoid multiple triggers. Default is 0 seconds.

        Raises:
             RuntimeError: If the host address could not be resolved.
        """
    def on_detect_all(self, callback: Callable[[dict], None]):
        '''Register a callback invoked for **every classification event**.

        This callback is useful if you want to process all classified labels in a single
        place, or be notified about any classification regardless of its type.

        Args:
            callback (Callable[[dict], None]):
                A function that accepts **exactly one argument**: a dictionary of
                classifications above the confidence threshold, in the form
                ``{"label": confidence, ...}``.

        Raises:
            TypeError: If `callback` is not a function.
            ValueError: If `callback` does not accept exactly one argument.
        '''
    def on_detect(self, object: str, callback: Callable[[], None]):
        '''Register a callback invoked when a **specific label** is classified.

        The callback is triggered whenever the given label appears in the classification
        results and passes the confidence and debounce filters.

        Args:
            object (str):
                The label to listen for (e.g., ``"dog"``).
            callback (Callable[[], None]):
                A function with **no parameters** that will be executed when the
                label is detected.

        Raises:
            TypeError: If `callback` is not a function.
            ValueError: If `callback` accepts one or more parameters.

        Notes:
            Registering a second callback for the same label overwrites the existing one.
        '''
    def start(self) -> None:
        """Start the classification."""
    def stop(self) -> None:
        """Stop the classification and release resources."""
    @brick.execute
    def classification_loop(self) -> None:
        """Classification main loop.

        Maintains WebSocket connection to the model runner and processes classification messages.
        Retries on connection errors until stopped.
        """
    @brick.execute
    def camera_loop(self) -> None:
        """Camera main loop.

        Captures images from the camera and forwards them over the TCP connection.
        Retries on connection errors until stopped.
        """
    def override_threshold(self, value: float):
        """Override the threshold for image classification model.

        Args:
            value (float): The new value for the threshold.

        Raises:
            TypeError: If the value is not a number.
            RuntimeError: If the model information is not available or does not support threshold override.
        """
