import numpy as np
from .camera import BaseCamera as BaseCamera
from .errors import CameraConfigError as CameraConfigError, CameraOpenError as CameraOpenError, CameraReadError as CameraReadError
from _typeshed import Incomplete
from arduino.app_utils import Logger as Logger
from collections.abc import Callable as Callable

logger: Incomplete

class IPCamera(BaseCamera):
    """
    IP Camera implementation for network-based cameras.

    Supports RTSP, HTTP, and HTTPS camera streams.
    Can handle authentication and various streaming protocols.
    """
    url: Incomplete
    username: Incomplete
    password: Incomplete
    timeout: Incomplete
    logger: Incomplete
    def __init__(self, url: str, username: str | None = None, password: str | None = None, timeout: int = 10, resolution: tuple[int, int] = (640, 480), fps: int = 10, adjustments: Callable[[np.ndarray], np.ndarray] | None = None, auto_reconnect: bool = True) -> None:
        """
        Initialize IP camera.

        Args:
            url: Camera stream URL (i.e. rtsp://..., http://..., https://...)
            username: Optional authentication username
            password: Optional authentication password
            timeout: Connection timeout in seconds
            resolution (tuple, optional): Resolution as (width, height). None uses default resolution.
            fps (int): Frames per second to capture from the camera.
            adjustments (callable, optional): Function or function pipeline to adjust frames that takes
                a numpy array and returns a numpy array. Default: None
            auto_reconnect (bool, optional): Enable automatic reconnection on failure. Default: True.
        """
