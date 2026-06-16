import abc
import numpy as np
import types
from .errors import CameraOpenError as CameraOpenError, CameraReadError as CameraReadError, CameraTransformError as CameraTransformError
from _typeshed import Incomplete
from abc import ABC
from arduino.app_utils import Logger as Logger
from collections.abc import Generator
from typing import Callable, Literal

logger: Incomplete

class BaseCamera(ABC, metaclass=abc.ABCMeta):
    """
    Abstract base class for camera implementations.

    This class defines the common interface that all camera implementations must follow,
    providing a unified API regardless of the underlying camera protocol or type.
    """
    resolution: Incomplete
    fps: Incomplete
    adjustments: Incomplete
    logger: Incomplete
    name: Incomplete
    auto_reconnect: Incomplete
    auto_reconnect_delay: float
    first_connection_max_retries: int
    def __init__(self, resolution: tuple[int, int] = (640, 480), fps: int = 10, adjustments: Callable[[np.ndarray], np.ndarray] | None = None, auto_reconnect: bool = True) -> None:
        """
        Initialize the camera base.

        Args:
            resolution (tuple, optional): Resolution as (width, height). None uses default resolution.
            fps (int): Frames per second to capture from the camera.
            adjustments (callable, optional): Function or function pipeline to adjust frames that takes
                a numpy array and returns a numpy array. Default: None.
            auto_reconnect (bool, optional): Enable automatic reconnection on failure. Default: True.
        """
    @property
    def status(self) -> Literal['disconnected', 'connected', 'streaming', 'paused']:
        """Read-only property for camera status."""
    def start(self) -> None:
        """
        Start the camera capture with retries, if enabled.

        Raises:
            CameraOpenError: If the camera fails to start after the retries.
            Exception: If the underlying implementation fails to start the camera.
        """
    def stop(self) -> None:
        """Stop the camera and release resources."""
    def capture(self) -> np.ndarray | None:
        """
        Capture a frame from the camera, respecting the configured FPS.

        Returns:
            Numpy array or None if no frame is available.

        Raises:
            CameraReadError: If the camera is not started.
            Exception: If the underlying implementation fails to read a frame.
        """
    def stream(self) -> Generator[Incomplete]:
        """
        Continuously capture frames from the camera.

        This is a generator that yields frames continuously while the camera is started.
        Built on top of capture() for convenience.

        Yields:
            np.ndarray: Video frames as numpy arrays.

        Raises:
            CameraReadError: If the camera is not started.
        """
    def record(self, duration) -> np.ndarray:
        """
        Record video for a specified duration and return it as a numpy array of raw frames.

        Args:
            duration (float): Recording duration in seconds.

        Returns:
            np.ndarray: numpy array of raw frames.

        Raises:
            CameraReadError: If camera is not started or any read error occurs.
            ValueError: If duration is not positive.
            MemoryError: If memory allocation for the full recording fails.
        """
    def record_avi(self, duration) -> np.ndarray:
        """
        Record video for a specified duration and return as MJPEG in AVI container.

        Args:
            duration (float): Recording duration in seconds.

        Returns:
            np.ndarray: AVI file containing MJPEG video.

        Raises:
            CameraReadError: If camera is not started or any read error occurs.
            ValueError: If duration is not positive.
            MemoryError: If memory allocation for the full recording fails.
        """
    def is_started(self) -> bool:
        """Check if the camera has been started."""
    def on_status_changed(self, callback: Callable[[str, dict], None] | None):
        '''Registers or removes a callback to be triggered on camera lifecycle events.

        When a camera status changes, the provided callback function will be invoked.
        If None is provided, the callback will be removed.

        Args:
            callback (Callable[[str, dict], None]): A callback that will be called every time the
                camera status changes with the new status and any associated data. The status names
                depend on the actual camera implementation being used. Some common events are:
                - \'connected\': The camera has been reconnected.
                - \'disconnected\': The camera has been disconnected.
                - \'streaming\': The stream is streaming.
                - \'paused\': The stream has been paused and is temporarily unavailable.
            callback (None): To unregister the current callback, if any.

        Example:
            def on_status(status: str, data: dict):
                print(f"Camera is now: {status}")
                print(f"Data: {data}")
                # Here you can add your code to react to the event

            camera.on_status_changed(on_status)
        '''
    def __enter__(self):
        """Context manager entry."""
    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: types.TracebackType | None) -> None:
        """Context manager exit."""
