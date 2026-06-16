from PIL import Image
from _typeshed import Incomplete
from arduino.app_peripherals.camera import CameraOpenError as COE, CameraReadError as CRE
from arduino.app_peripherals.camera.v4l_camera import V4LCamera as V4LCamera
from arduino.app_utils import Logger as Logger
from arduino.app_utils.image import compressed_to_png as compressed_to_png, letterboxed as letterboxed, numpy_to_pil as numpy_to_pil

logger: Incomplete
CameraReadError = CRE
CameraOpenError = COE

class USBCamera:
    """Represents an input peripheral for capturing images from a USB camera device.
    This class uses OpenCV to interface with the camera and capture images.
    """
    compression: Incomplete
    def __init__(self, camera: int = 0, resolution: tuple[int, int] = None, fps: int = 10, compression: bool = False, letterbox: bool = False) -> None:
        """Initialize the USB camera.

        Args:
            camera (int): Camera index (default is 0 - index is related to the first camera available from /dev/v4l/by-id devices).
            resolution (tuple[int, int]): Resolution as (width, height). If None, uses default resolution.
            fps (int): Frames per second for the camera. If None, uses default FPS.
            compression (bool): Whether to compress the captured images. If True, images are compressed to PNG format.
            letterbox (bool): Whether to apply letterboxing to the captured images.
        """
    def capture(self) -> Image.Image | None:
        """Captures a frame from the camera, blocking to respect the configured FPS.

        Returns:
            PIL.Image.Image | None: The captured frame as a PIL Image, or None if no frame is available.
        """
    def capture_bytes(self) -> bytes | None:
        """Captures a frame from the camera and returns its raw bytes, blocking to respect the configured FPS.

        Returns:
            bytes | None: The captured frame as a bytes array, or None if no frame is available.
        """
    def start(self) -> None:
        """Starts the camera capture."""
    def stop(self) -> None:
        """Stops the camera and releases its resources."""
    def produce(self):
        """Alias for capture method."""
