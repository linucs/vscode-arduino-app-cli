import numpy as np
from .base_camera import BaseCamera as BaseCamera
from .errors import CameraConfigError as CameraConfigError
from .utils import nth_plugged_camera as nth_plugged_camera
from collections.abc import Callable as Callable

class Camera:
    """
    Unified Camera class that can be configured for different camera types.

    This class serves as both a factory and a wrapper, automatically creating
    the appropriate camera implementation based on the provided configuration.

    Supports:
        - USB Cameras (local cameras connected using USB interface)
        - CSI Cameras (local cameras connected using MIPI CSI-2 interface)
        - IP Cameras (network-based cameras via RTSP, HLS)
        - WebSocket Cameras (input video streams via WebSocket client)

    Note: constructor arguments (except those in signature) must be provided in
    keyword format to forward them correctly to the specific camera implementations.
    """
    def __new__(cls, source: str | int = 0, resolution: tuple[int, int] = (640, 480), fps: int = 10, adjustments: Callable[[np.ndarray], np.ndarray] | None = None, **kwargs) -> BaseCamera:
        '''
        Create a camera instance based on the source type.

        Args:
            source (Union[str, int]): Camera source identifier. Supports:
                - int: Auto-select the n-th available physically connected camera
                    giving priority to USB cameras, then CSI cameras if supported
                    by the platform
                - str: V4L camera ordinal index (e.g., "usb:0", "usb:1")
                - str: V4L camera device path (e.g., "usb:/dev/video0",
                    "usb:/dev/v4l/by-id/...", "usb:/dev/v4l/by-path/...
                    the "usb:" prefix is optional)
                - str: CSI camera ordinal index (e.g., "csi:0", "csi:1")
                - str: CSI camera name (e.g., "csi:CAMERA0", "csi:CAMERA1")
                - str: URL for IP cameras (e.g., "rtsp://...", "http://...")
                - str: WebSocket URL for input streams (e.g., "ws://0.0.0.0:8080")
                Default: 0.
            resolution (tuple[int, int]): Frame resolution as (width, height).
                Default: (640, 480).
            fps (int): Target frames per second. Default: 10.
            adjustments (callable, optional): Function pipeline to adjust frames
                that takes a numpy array and returns a numpy array. Default: None.
            **kwargs: Camera-specific configuration parameters grouped by type:
                V4L Camera Parameters:
                    device (int | str): V4L device. Default: 0.
                    codec (str, optional): Video codec to use (FourCC). Options: "YUVY",
                            "MJPG", "H264". Default: "" (auto).
                CSI Camera Parameters:
                    device (int | str): CSI device. Default: 0.
                IP Camera Parameters:
                    url (str): Camera stream URL.
                    username (str, optional): Authentication username.
                    password (str, optional): Authentication password.
                    timeout (float): Connection timeout in seconds. Default: 10.0.
                WebSocket Camera Parameters:
                    port (int): Port to bind the server to. Default: 8080.
                    timeout (int): Connection timeout in seconds. Default: 3.
                    certs_dir_path (str): Path to directory containing TLS certificates.
                        Default: "/app/certs".
                    use_tls (bool): Enable TLS for secure connections. If True, \'encrypt\'
                        will be ignored. Default: False.
                    secret (str): Secret key for authentication/encryption. Empty string
                        disables security. Default: "".
                    encrypt (bool): Enable encryption (only effective if secret is provided).
                        Default: False.
                    auto_reconnect (bool): Whether to automatically attempt to reconnect
                        if the camera connection is lost. Default: True.

        Returns:
            BaseCamera: Appropriate camera implementation instance

        Raises:
            CameraConfigError: If source type is not supported or parameters are invalid
            CameraOpenError: If the camera cannot be opened

        Examples:
            V4L Camera:

            ```python
            camera = Camera("usb:0", resolution=(640, 480), fps=30)
            camera = Camera("usb:/dev/video1", fps=15)
            ```

            CSI Camera:

            ```python
            camera = Camera("csi:0", resolution=(640, 480), fps=30)
            camera = Camera("csi:CAMERA1", fps=15)
            ```

            IP Camera:

            ```python
            camera = Camera("rtsp://192.168.1.100:554/stream")
            camera = Camera("http://192.168.1.100:8080/video.mp4", username="admin", password="secret")
            ```

            WebSocket Camera:

            ```python
            camera = Camera("ws://0.0.0.0:8080")
            camera = Camera("ws://0.0.0.0:8080", secret="my_secret", encrypt=True)
            camera = Camera("ws://0.0.0.0:8080", use_tls=True, certs_dir_path="/path/to/certs")
            ```
        '''
