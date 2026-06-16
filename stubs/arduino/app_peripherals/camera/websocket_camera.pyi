import numpy as np
from .base_camera import BaseCamera as BaseCamera
from .errors import CameraConfigError as CameraConfigError, CameraOpenError as CameraOpenError
from _typeshed import Incomplete
from arduino.app_internal.core.peripherals import BPPCodec as BPPCodec
from arduino.app_utils import Logger as Logger
from collections.abc import Callable as Callable

logger: Incomplete

class WebSocketCamera(BaseCamera):
    '''
    WebSocket Camera implementation that hosts a WebSocket server.

    This camera acts as a WebSocket server that receives frames from a connected
    client. Only one client can be connected at a time.

    The client must encode video frames in one of these formats:
    - JPEG
    - PNG
    - WebP
    - BMP
    - TIFF

    Communication uses the BPP (Binary Peripheral Protocol) in three security modes:
    - Security disabled (secret=None) - BPP with no authentication
    - Authenticated (secret + encrypt=False) - BPP with HMAC-SHA256
    - Authenticated + Encrypted (secret + encrypt=True) - BPP with ChaCha20-Poly1305

    By default, all modes use BPP framing. When security is disabled (secret=None),
    clients can opt out of BPP by connecting with the "raw=true" URL query parameter,
    allowing them to send raw image bytes directly without BPP wrapping. This parameter
    is silently ignored when security is enabled.

    When connecting, clients can specify a "client_name" parameter in the URL query string
    to identify themselves. This name will be sanitized to allow only alphanumeric chars,
    whitespace, hyphens, and underscores, and limit its length to 64 characters.
    '''
    codec: Incomplete
    secret: Incomplete
    encrypt: Incomplete
    logger: Incomplete
    name: Incomplete
    use_tls: Incomplete
    protocol: Incomplete
    ip: Incomplete
    port: Incomplete
    timeout: Incomplete
    def __init__(self, port: int = 8080, timeout: int = 3, certs_dir_path: str = '/app/certs', use_tls: bool = False, secret: str | None = None, encrypt: bool = False, resolution: tuple[int, int] = (640, 480), fps: int = 10, adjustments: Callable[[np.ndarray], np.ndarray] | None = None, auto_reconnect: bool = True) -> None:
        """
        Initialize WebSocket camera server with security options.

        Args:
            port (int): Port to bind the server to
            timeout (int): Connection timeout in seconds
            certs_dir_path (str): Path to the directory containing TLS certificates
            use_tls (bool): Enable TLS for secure connections. If True, 'encrypt' will
                be ignored. Use this for transport-level security with clients that can
                accept self-signed certificates or when supplying your own certificates.
            secret (str | None): Pre-shared secret key used for HMAC-SHA256
                authentication, or to derive the ChaCha20-Poly1305 key when
                encrypt is True. None disables security. Default: None.
            encrypt (bool): Enable ChaCha20-Poly1305 encryption. Requires a
                non-None secret; raises RuntimeError otherwise. Default: False.
            resolution (tuple[int, int]): Resolution as (width, height)
            fps (int): Frames per second to capture
            adjustments (Callable[[np.ndarray], np.ndarray] | None): Function to adjust frames
            auto_reconnect (bool): Enable automatic reconnection on failure
        """
    @property
    def url(self) -> str:
        """Return the WebSocket server address."""
    @property
    def security_mode(self) -> str:
        """Return current security mode for logging/debugging."""
