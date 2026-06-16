import numpy as np
from .camera import BaseCamera as BaseCamera
from .errors import CameraOpenError as CameraOpenError, CameraReadError as CameraReadError
from _typeshed import Incomplete
from arduino.app_utils import Logger as Logger
from collections.abc import Callable as Callable
from typing import Literal

logger: Incomplete

class V4LCamera(BaseCamera):
    """
    V4L (Video4Linux) camera implementation for physically connected cameras.

    This class handles USB cameras and other V4L-compatible devices on Linux systems.
    """
    codec: Incomplete
    v4l_path: Incomplete
    name: Incomplete
    logger: Incomplete
    def __init__(self, device: str | int = 0, resolution: tuple[int, int] = (640, 480), fps: int = 10, adjustments: Callable[[np.ndarray], np.ndarray] | None = None, auto_reconnect: bool = True, codec: Literal['', 'YUVY', 'MJPG', 'H264'] = '') -> None:
        '''
        Initialize V4L camera.

        Args:
            device: Camera identifier in the form of either:
                - int: Camera ordinal index (e.g., 0, 1)
                - str: Camera ordinal index as string (e.g., "0", "1")
                - str: Camera device path (e.g., "/dev/video0", "/dev/v4l/by-id/...",
                    "/dev/v4l/by-path/...")
                Default: 0 (first available USB camera).
            resolution (tuple[int, int]): Resolution as (width, height). None uses default resolution.
            fps (int): Frames per second to capture from the camera. Default: 10.
            adjustments (callable, optional): Function or function pipeline to adjust frames that takes
                a numpy array and returns a numpy array. Default: None
            auto_reconnect (bool): Enable automatic reconnection on failure. Default: True.
            codec (str, optional): Video codec to use (FourCC). Options: "YUVY", "MJPG", "H264".
                Default: "" (auto).
        '''
    @staticmethod
    def list_devices() -> list[int]:
        """
        Return a list of available USB cameras.

        Returns:
            list[int]: List of USB camera indices.
        """
