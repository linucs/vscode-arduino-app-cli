import numpy as np
from PIL.Image import Image as Image
from _typeshed import Incomplete
from arduino.app_peripherals.camera import BaseCamera as BaseCamera, Camera as Camera
from arduino.app_utils import Logger as Logger, brick as brick
from arduino.app_utils.image import greyscale as greyscale, numpy_to_pil as numpy_to_pil
from dataclasses import dataclass
from typing import Callable

logger: Incomplete
barcodes_only: Incomplete
qrcodes_only: Incomplete

@dataclass
class Detection:
    '''This class represents a single QR code or barcode detection result from a video frame.

    This data structure holds the decoded content, the type of code, and its location
    in the image as determined by the detection algorithm.

    Attributes:
        content (str): The decoded string extracted from the QR code or barcode.
        type (str): The type of code detected, typically "QRCODE" or "BARCODE".
        coords (np.ndarray): A NumPy array of shape (4, 2) representing the four corner
            points (x, y) of the detected code region in the image.
    '''
    content: str
    type: str
    coords: np.ndarray

class CameraCodeDetection:
    """Scans a camera video feed for QR codes and/or barcodes.

    Args:
        camera (BaseCamera): The camera instance to use for capturing video. If None, a default camera will be initialized.
        detect_qr (bool): Whether to detect QR codes. Defaults to True.
        detect_barcode (bool): Whether to detect barcodes. Defaults to True.

    Raises:
        ValueError: If both detect_qr and detect_barcode are False.
        RuntimeError: If there is an error during initialization.
    """
    already_seen_codes: Incomplete
    def __init__(self, camera: BaseCamera = None, detect_qr: bool = True, detect_barcode: bool = True) -> None:
        """Initialize the CameraCodeDetection brick."""
    def start(self) -> None:
        """Start the detector and begin scanning for codes."""
    def stop(self) -> None:
        """Stop the detector and release resources."""
    def on_detect(self, callback: Callable[[Image, list[Detection]], None] | Callable[[Image, Detection], None] | None):
        '''Registers or removes a callback to be triggered on code detection.

        When a QR code or barcode is detected in the camera feed, the provided callback function will be invoked.
        The callback function should accept the Image frame and a list[Detection] or Detection objects. If the former
        is used, it will receive all detections at once. If the latter is used, it will be called once for each
        detection. If None is provided, the callback will be removed.

        Args:
            callback (Callable[[Image, list[Detection]], None]): A callback that will be called every time a detection
                                                                 is made with all the detections.
            callback (Callable[[Image, Detection], None]): A callback that will be called every time a detection is
                                                           made with a single detection.
            callback (None): To unregister the current callback, if any.

        Example:
            def on_code_detected(frame: Image, detection: Detection):
                print(f"Detected {detection.type} with content: {detection.content}")
                # Here you can add your code to process the detected code,
                # e.g., draw a bounding box, save it to a database or log it.

            detector.on_detect(on_code_detected)
        '''
    def on_frame(self, callback: Callable[[Image], None] | None):
        """Registers a callback function to be called when a new camera frame is captured.

        The callback function should accept the Image frame.
        If None is provided, the callback is removed.

        Args:
            callback (Callable[[Image], None]): A callback that will be called with each captured frame.
            callback (None): Signals to remove the current callback, if any.
        """
    def on_error(self, callback: Callable[[Exception], None] | None):
        """Registers a callback function to be called when an error occurs in the detector.

        The callback function should accept the exception as an argument.
        If None is provided, the callback is removed.

        Args:
            callback (Callable): A callback that will be called with the exception raised in the detector.
            callback (None): Signals to remove the current callback, if any.
        """
    def loop(self) -> None:
        """Main loop to capture frames and detect codes."""
