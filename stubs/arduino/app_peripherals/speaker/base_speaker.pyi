import abc
import numpy as np
import types
from .errors import SpeakerConfigError as SpeakerConfigError, SpeakerOpenError as SpeakerOpenError, SpeakerWriteError as SpeakerWriteError
from _typeshed import Incomplete
from abc import ABC
from arduino.app_utils import Logger as Logger
from collections.abc import Callable as Callable
from typing import Literal

logger: Incomplete
type FormatPlain = type | np.dtype | str
type FormatPacked = tuple[FormatPlain, bool]

class BaseSpeaker(ABC, metaclass=abc.ABCMeta):
    """
    Abstract base class for speaker implementations.

    This class defines the common interface that all speaker implementations must follow,
    providing a unified API regardless of the underlying audio playback protocol or type.

    The input is always a NumPy array with the PCM format.
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
        Initialize the speaker base.

        Args:
            sample_rate (int): Sample rate in Hz.
            channels (int): Number of audio channels.
            format (FormatPlain | FormatPacked): Audio format as one of:
                - Type classes: np.int16, np.float32, np.uint8
                - dtype objects: np.dtype('<i2'), np.dtype('>f4')
                - Strings: 'int16', '<i2', '>f4', 'float32'
                - Tuple of (format, is_packed): to specify if the format is packed (e.g. 24-bit audio)
            buffer_size (int): Size of the audio buffer.
            auto_reconnect (bool, optional): Enable automatic reconnection on failure. Default: True.

        Raises:
            SpeakerConfigError: If the provided configuration is not valid.
        """
    @property
    def volume(self) -> int:
        """
        Get or set the speaker volume level.

        This controls the software volume of the speaker device.

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
    def status(self) -> Literal['disconnected', 'connected']:
        """Read-only property for camera status."""
    def start(self) -> None:
        """Start the speaker capture."""
    def stop(self) -> None:
        """Stop the speaker and release resources."""
    def play(self, audio_chunk: np.ndarray):
        """
        Play an audio chunk on the speaker.

        Args:
            audio_chunk (np.ndarray): NumPy array in PCM format.

        Raises:
            SpeakerWriteError: If the speaker is not started.
            ValueError: If audio_chunk is empty or invalid.
            Exception: If the underlying implementation fails to write a frame.
        """
    def play_pcm(self, pcm_audio: np.ndarray) -> None:
        """
        Play raw PCM audio data.

        Args:
            pcm_audio (np.ndarray): Raw PCM audio data in PCM format.

        Raises:
            SpeakerOpenError: If speaker can't be opened or reopened.
            SpeakerWriteError: If speaker is not started.
            ValueError: If pcm_audio is empty or invalid.
            Exception: If the underlying implementation fails to write a frame.
        """
    def play_wav(self, wav_audio: np.ndarray) -> None:
        """
        Play audio from WAV format data.
        Note: Only uncompressed PCM WAV files are supported.

        Args:
            wav_audio (np.ndarray): WAV format audio data (including header).

        Raises:
            SpeakerOpenError: If speaker can't be opened or reopened.
            SpeakerWriteError: If speaker is not started.
            ValueError: If wav_audio is empty or invalid.
            Exception: If the underlying implementation fails to write a frame.
        """
    def is_started(self) -> bool:
        """Check if the speaker is started."""
    def on_status_changed(self, callback: Callable[[str, dict], None] | None):
        '''Registers or removes a callback to be triggered on speaker lifecycle events.

        When a speaker status changes, the provided callback function will be invoked.
        If None is provided, the callback will be removed.

        Args:
            callback (Callable[[str, dict], None]): A callback that will be called every time the
                speaker status changes with the new status and any associated data. The status
                names depend on the actual speaker implementation being used. Some common events
                are:
                - \'connected\': The speaker has been reconnected.
                - \'disconnected\': The speaker has been disconnected.
            callback (None): To unregister the current callback, if any.

        Example:
            def on_status(status: str, data: dict):
                print(f"Speaker is now: {status}")
                print(f"Data: {data}")
                # Here you can add your code to react to the event

            speaker.on_status_changed(on_status)
        '''
    def __enter__(self):
        """Context manager entry."""
    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: types.TracebackType | None) -> None:
        """Context manager exit."""
