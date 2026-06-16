import types
from _typeshed import Incomplete
from arduino.app_internal.core import get_brick_config as get_brick_config, get_brick_configured_model as get_brick_configured_model, resolve_address as resolve_address
from arduino.app_peripherals.speaker import BaseSpeaker as BaseSpeaker, Speaker as Speaker
from arduino.app_utils import Logger as Logger, brick as brick
from collections.abc import Generator, Iterator
from typing import ContextManager

logger: Incomplete
TTS_MAX_CHARS: int

class TTSError(Exception):
    """Base class for TTS errors."""
class TTSBusyError(TTSError):
    """Raised when this TTS instance already has an active speech session."""

class SynthesisStream(ContextManager['SynthesisStream'], Iterator[bytes]):
    """Iterator wrapper that guarantees proper teardown on context exit."""
    def __init__(self, generator: Generator[bytes, None, None]) -> None: ...
    def __enter__(self) -> SynthesisStream: ...
    def __exit__(self, exc_type: type[BaseException] | None, exc: BaseException | None, tb: types.TracebackType | None) -> None: ...
    def __iter__(self) -> SynthesisStream: ...
    def __next__(self) -> bytes: ...
    def close(self) -> None: ...

class TextToSpeech:
    """Text-to-Speech brick for offline speech synthesis using local TTS service."""
    api_host: Incomplete
    api_port: int
    api_base_url: Incomplete
    def __init__(self, speaker: BaseSpeaker | None = None) -> None:
        """Initialize the TextToSpeech brick.
        Args:
            speaker (BaseSpeaker, optional): Speaker instance to use for audio output. If not provided, a default Speaker will be used.
        """
    def start(self) -> None:
        """Start the TextToSpeech brick by initializing the speaker."""
    def stop(self) -> None:
        """Stop the TextToSpeech brick by stopping the speaker."""
    def cancel(self) -> None:
        """Cancel active speech playback, if any, without stopping the speaker."""
    def speak(self, text: str):
        """
        Synthesize speech from text and play it through the provided speaker.
        Long text is split into 1024-character chunks before synthesis.

        Args:
            text (str): The text to be synthesized into speech.

        Raises:
            TTSBusyError: If this instance already has an active speech session.
            RuntimeError: If the synthesis fails.
        """
    def synthesize_wav(self, text: str) -> bytes:
        """
        Synthesize speech from text and return the audio in WAV format.

        Args:
            text (str): The text to be synthesized into speech.

        Returns:
            bytes: The synthesized audio in WAV format.

        Raises:
            TTSBusyError: If this instance already has an active speech session.
            RuntimeError: If the synthesis fails.
        """
    def synthesize_pcm(self, text: str) -> bytes:
        """
        Synthesize speech from text and return the audio in PCM format (mono, 16-bit, 44.1kHz).

        Args:
            text (str): The text to be synthesized into speech.

        Returns:
            bytes: The synthesized audio in PCM format.

        Raises:
            TTSBusyError: If this instance already has an active speech session.
            RuntimeError: If the synthesis fails.
        """
    def synthesize_pcm_stream(self, text: str) -> SynthesisStream:
        """
        Synthesize speech from text and stream PCM audio chunks as they arrive.

        Args:
            text (str): The text to be synthesized into speech.

        Returns:
            SynthesisStream: An iterable/context-manager yielding PCM audio chunks. Use as a
                ``with`` block to guarantee teardown of the underlying HTTP response and
                release of the session lock.

        Raises:
            TTSBusyError: If this instance already has an active speech session.
            RuntimeError: If the synthesis fails.
        """
