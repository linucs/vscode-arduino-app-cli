import abc
import numpy as np
import types
from .errors import MicrophoneConfigError as MicrophoneConfigError, MicrophoneOpenError as MicrophoneOpenError, MicrophoneReadError as MicrophoneReadError
from _typeshed import Incomplete
from abc import ABC
from arduino.app_utils import Logger as Logger
from collections.abc import Callable as Callable, Generator
from typing import Literal

logger: Incomplete
type FormatPlain = type | np.dtype | str
type FormatPacked = tuple[FormatPlain, bool]

class BaseMicrophone(ABC, metaclass=abc.ABCMeta):
    """
    Abstract base class for microphone implementations.

    This class defines the common interface that all microphone implementations must follow,
    providing a unified API regardless of the underlying audio capture protocol or type.

    The output is always a NumPy array with the ALSA PCM format.
    """
    sample_rate: Incomplete
    channels: Incomplete
    format_is_packed: bool
    format: np.dtype
    buffer_size: Incomplete
    logger: Incomplete
    name: Incomplete
    auto_reconnect: Incomplete
    auto_reconnect_delay: float
    first_connection_max_retries: int
    def __init__(self, sample_rate: int, channels: int, format: FormatPlain | FormatPacked, buffer_size: int, auto_reconnect: bool) -> None:
        """
        Initialize the microphone base.

        Args:
            sample_rate (int): Sample rate in Hz (default: 16000).
            channels (int): Number of audio channels (default: 1).
            format (FormatPlain | FormatPacked): Audio format as one of:
                - Type classes: np.int16, np.float32, np.uint8
                - dtype objects: np.dtype('<i2'), np.dtype('>f4')
                - Strings: 'int16', '<i2', '>f4', 'float32'
                - Tuple of (format, is_packed): to specify if the format is packed (e.g. 24-bit audio)
            buffer_size (int): Size of the audio buffer.
            auto_reconnect (bool, optional): Enable automatic reconnection on failure. Default: True.
        """
    @property
    def volume(self) -> int:
        """
        Get or set the microphone volume level.

        This controls the software volume of the microphone device.

        Args:
            volume (int): Software volume level (0-100).

        Returns:
            int: Current volume level (0-100).

        Raises:
            ValueError: If the volume is not valid.
        """
    @volume.setter
    def volume(self, volume: int): ...
    @property
    def status(self) -> Literal['disconnected', 'connected', 'streaming', 'paused']:
        """Read-only property for camera status."""
    def start(self) -> None:
        """Start the microphone capture."""
    def stop(self) -> None:
        """Stop the microphone and release resources."""
    def capture(self) -> np.ndarray | None:
        """
        Capture an audio chunk from the microphone.

        Returns:
            Numpy array in ALSA PCM format or None if no audio is available.

        Raises:
            MicrophoneReadError: If the microphone is not started.
            Exception: If the underlying implementation fails to read a frame.
        """
    def stream(self) -> Generator[Incomplete]:
        """
        Continuously capture audio chunks from the microphone.

        This is a generator that yields audio chunks continuously while the microphone is started.

        Yields:
            np.ndarray: Audio chunks as numpy arrays.
        """
    def is_started(self) -> bool:
        """Check if the microphone is started."""
    def on_status_changed(self, callback: Callable[[str, dict], None] | None):
        '''Registers or removes a callback to be triggered on microphone lifecycle events.

        When a microphone status changes, the provided callback function will be invoked.
        If None is provided, the callback will be removed.

        Args:
            callback (Callable[[str, dict], None]): A callback that will be called every time the
                microphone status changes with the new status and any associated data. The status
                names depend on the actual microphone implementation being used. Some common events
                are:
                - \'connected\': The microphone has been reconnected.
                - \'disconnected\': The microphone has been disconnected.
                - \'streaming\': The stream is streaming.
                - \'paused\': The stream has been paused and is temporarily unavailable.
            callback (None): To unregister the current callback, if any.

        Example:
            def on_status(status: str, data: dict):
                print(f"Microphone is now: {status}")
                print(f"Data: {data}")
                # Here you can add your code to react to the event

            microphone.on_status_changed(on_status)
        '''
    def record_pcm(self, duration: float) -> np.ndarray:
        """
        Record audio for a specified duration and return as raw PCM format.

        Args:
            duration (float): Recording duration in seconds.

        Returns:
            np.ndarray: Raw audio data in raw ALSA PCM format.

        Raises:
            MicrophoneOpenError: If microphone can't be opened or reopened.
            MicrophoneReadError: If no audio is available after multiple attempts.
            ValueError: If duration is not > 0.
            Exception: If the underlying implementation fails to read a frame.
        """
    def record_wav(self, duration: float) -> np.ndarray:
        """
        Record audio for a specified duration and return as WAV format.
        Note: Only uncompressed PCM WAV recordings are supported.

        Args:
            duration (float): Recording duration in seconds.

        Returns:
            np.ndarray: Raw audio data in WAV format as numpy array.

        Raises:
            MicrophoneOpenError: If microphone can't be opened or reopened.
            MicrophoneReadError: If no audio is available after multiple attempts.
            ValueError: If duration is not > 0.
            Exception: If the underlying implementation fails to read a frame.
        """
    def __enter__(self):
        """Context manager entry."""
    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: types.TracebackType | None) -> None:
        """Context manager exit."""
