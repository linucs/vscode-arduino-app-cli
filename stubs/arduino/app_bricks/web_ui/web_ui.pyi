from _typeshed import Incomplete
from arduino.app_peripherals.camera.base_camera import BaseCamera as BaseCamera
from arduino.app_utils import Logger as Logger, brick as brick
from collections.abc import Callable as Callable
from typing import Any

logger: Incomplete

class WebUI:
    """Module for deploying a web server that can host a web application and expose APIs to its clients.

    It uses FastAPI, Uvicorn, and Socket.IO to serve static files (e.g., HTML/CSS/JS), handle REST API endpoints,
    and support real-time communication between the client and the server.

    """
    app: Incomplete
    sio: Incomplete
    def __init__(self, addr: str = '0.0.0.0', port: int = 7000, ui_path_prefix: str = '', api_path_prefix: str = '', assets_dir_path: str = '/app/assets', certs_dir_path: str = '/app/certs', use_tls: bool = False, use_ssl: bool | None = None, cors_origins: str = '*') -> None:
        '''Initialize the web server.

        Args:
            addr (str, optional): Server bind address. Defaults to "0.0.0.0" (all interfaces).
            port (int, optional): Server port number. Defaults to 7000.
            ui_path_prefix (str, optional): URL prefix for UI routes. Defaults to "" (root).
            api_path_prefix (str, optional): URL prefix for API routes. Defaults to "" (root).
            assets_dir_path (str, optional): Path to static assets directory. Defaults to "/app/assets".
            certs_dir_path (str, optional): Path to TLS certificates directory. Defaults to "/app/certs".
            use_tls (bool, optional): Enable TLS/HTTPS. Defaults to False.
            use_ssl (bool, optional): Deprecated. Use use_tls instead. Defaults to None.
            cors_origins (str, optional): CORS allowed origins. Can be "*" for all origins, a
                comma-separated list of origins, or an empty string to disable CORS. Defaults to "*".
        '''
    @property
    def local_url(self) -> str:
        """Get the locally addressable URL of the web server.

        Returns:
            str: The server's URL (including protocol, address, and port).
        """
    @property
    def url(self) -> str:
        """Get the externally addressable URL of the web server.

        Returns:
            str: The server's URL (including protocol, address, and port).
        """
    def start(self) -> None:
        """Start the web server asynchronously.

        This sets up static file routing and WebSocket event handlers, configures TLS if enabled, and launches the server using Uvicorn.

        Raises:
            RuntimeError: If 'index.html' is missing in the static assets directory.
            RuntimeError: If TLS is enabled but certificates fail to generate.
            RuntimeWarning: If the server is already running.
        """
    def stop(self) -> None:
        """Stop the web server gracefully.

        Waits up to 5 seconds for current requests to finish before terminating.
        """
    def execute(self) -> None: ...
    def expose_api(self, method: str, path: str, function: Callable):
        '''Register a route with the specified HTTP method and path.

        The path will be prefixed with the api_path_prefix configured during initialization.

        Args:
            method (str): HTTP method to use (e.g., "GET", "POST").
            path (str): URL path for the API endpoint (without the prefix).
            function (Callable): Function to execute when the route is accessed.
        '''
    def expose_camera(self, path: str, camera: BaseCamera, jpeg_quality: int = 80):
        """
        Expose a camera stream at the specified URL path in MJPEG format.

        This can be consumed for example using `<img>` tags in a web application.

        Args:
            path (str): URL path for the MJPEG stream endpoint.
            camera (BaseCamera): A camera instance, will be started if not already running.
            jpeg_quality (int, optional): JPEG compression quality (0-100). Default: 80.
        """
    def on_connect(self, callback: Callable[[str], None]):
        """Register a callback for WebSocket connection events.

        The callback should accept a single argument: the session ID (sid) of the connected client.

        Args:
            callback (Callable[[str], None]): Function to call when a client connects. Receives the session ID (sid) as its only argument.

        """
    def on_disconnect(self, callback: Callable[[str], None]):
        """Register a callback for WebSocket disconnection events.

        The callback should accept a single argument: the session ID (sid) of the disconnected client.

        Args:
            callback (Callable[[str], None]): Function to call when a client disconnects. Receives the session ID (sid) as its only argument.

        """
    def on_message(self, message_type: str, callback: Callable[[str, Any], Any]):
        '''Register a callback function for a specific WebSocket message type received by clients.

        The client should send messages named as message_type for this callback to be triggered.

        If a response is returned by the callback, it will be sent back to the client
        with a message type suffix "_response".

        Args:
            message_type (str): The message type name to listen for.
            callback (Callable[[str, Any], Any]): Function to handle the message. Receives two arguments:
                the session ID (sid) and the incoming message data.

        '''
    def send_message(self, message_type: str, message: dict | str, room: str | None = None):
        """Send a message to connected WebSocket clients.

        Args:
            message_type (str): The name of the message event to emit.
            message (dict | str): The message payload to send (dict or str).
            room (str): The target Socket.IO room (defaults to all clients).

        """
