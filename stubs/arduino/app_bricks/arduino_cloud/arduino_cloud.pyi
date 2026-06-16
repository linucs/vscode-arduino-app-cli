from _typeshed import Incomplete
from arduino.app_utils import Logger as Logger, brick as brick
from typing import Any

logger: Incomplete

class ArduinoCloud:
    """Arduino Cloud client for managing devices and data."""
    def __init__(self, device_id: str = ..., secret: str = ..., server: str = 'iot.arduino.cc', port: int = 8884) -> None:
        '''Initialize the Arduino Cloud client.

        Args:
            device_id (str): The unique identifier for the device.
                             If omitted, uses ARDUINO_DEVICE_ID environment variable.
            secret (str): The password for Arduino Cloud authentication.
                          If omitted, uses ARDUINO_SECRET environment variable.
            server (str, optional): The server address for Arduino Cloud (default: "iot.arduino.cc").
            port (int, optional): The port to connect to the Arduino Cloud server (default: 8884).

        Raises:
            ValueError: If either device_id or secret is not provided explicitly or via environment variable.

        '''
    def start(self) -> None:
        """Start the Arduino IoT Cloud client."""
    def loop(self) -> None:
        """Run a single iteration of the Arduino IoT Cloud client loop, processing commands and updating state."""
    def register(self, aiotobj: str | Any, **kwargs: Any):
        """Register a variable or object with the Arduino Cloud client.

        Args:
            aiotobj (str | Any): The variable name or object from which to derive the variable name to register.
            **kwargs (Any): Additional keyword arguments for registration.
        """
    def __getattr__(self, name: str):
        """Intercept access to cloud variables as natural attributes."""
    def __setattr__(self, name: str, value: Any):
        """Intercept assignment to cloud variables as natural attributes."""
