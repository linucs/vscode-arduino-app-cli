import numpy as np
from .camera import BaseCamera as BaseCamera
from .errors import CameraOpenError as CameraOpenError, CameraReadError as CameraReadError
from .media_graph import find_camss_media_device as find_camss_media_device, find_sensor_i2c_addr as find_sensor_i2c_addr, scan_sensor_i2c_addresses as scan_sensor_i2c_addresses
from .utils import resolve_camera_name as resolve_camera_name
from _typeshed import Incomplete
from arduino.app_utils import Logger as Logger
from collections.abc import Callable as Callable

logger: Incomplete

class CSICamera(BaseCamera):
    """
    CSI (Camera Serial Interface) camera implementation for physically connected cameras.

    This class handles CSI cameras on Linux systems.
    """
    media_dev: Incomplete
    csi_path: Incomplete
    name: Incomplete
    logger: Incomplete
    def __init__(self, device: str | int = 0, resolution: tuple[int, int] = (1280, 720), fps: int = 30, adjustments: Callable[[np.ndarray], np.ndarray] | None = None, auto_reconnect: bool = True) -> None:
        '''
        Initialize CSI camera.

        Args:
            device: Camera identifier in the form of either:
                - int: Camera ordinal index (e.g., 0, 1)
                - str: Camera ordinal index as string (e.g., "0", "1")
                - str: Camera name (e.g., "CAMERA0", "CAMERA1")
                Default: 0 (first available CSI camera).
            resolution (tuple, optional): Resolution as (width, height). None uses default resolution.
            fps (int, optional): Frames per second to capture from the camera. Default: 10.
            adjustments (callable, optional): Function or function pipeline to adjust frames that takes
                a numpy array and returns a numpy array. Default: None.
            auto_reconnect (bool, optional): Enable automatic reconnection on failure. Default: True.
        '''
    @staticmethod
    def list_devices() -> list[int]:
        """
        Return a sorted list of available CSI cameras.

        Returns:
            list[int]: List of CSI camera indices.
        """
    @staticmethod
    def list_device_names() -> list[str]:
        """
        Return a list of available CSI cameras.

        Returns:
            list[str]: List of CSI camera device paths.
        """
