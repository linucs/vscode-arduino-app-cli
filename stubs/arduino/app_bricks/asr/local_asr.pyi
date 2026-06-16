import numpy as np
import queue
import threading
import types
from _typeshed import Incomplete
from arduino.app_internal.core import resolve_address as resolve_address
from arduino.app_internal.core.module import get_brick_config as get_brick_config, get_brick_configured_model as get_brick_configured_model
from arduino.app_peripherals.microphone import BaseMicrophone as BaseMicrophone, Microphone as Microphone
from arduino.app_utils import Logger as Logger, brick as brick
from collections.abc import Generator, Iterator
from dataclasses import dataclass
from typing import ContextManager, Generic, Literal, TypeVar

logger: Incomplete

class ASRError(Exception):
    """Base class for ASR errors."""
class ASRBusyError(ASRError):
    """Raised when this ASR instance already has an active transcription session."""
class ASRServiceBusyError(ASRError):
    """Raised when the inference server rejects session creation because it is serving another client."""
class ASRUnavailableError(ASRError):
    """Raised when the inference service is unreachable or the connection drops unexpectedly."""
class AudioSourceExhausted(Exception):
    """
    Raised by finite-source adapters (WAV/ndarray) to signal end-of-data.
    Never raised by real BaseMicrophone implementations.
    """

@dataclass(frozen=True)
class ASREvent:
    type: Literal['partial_text', 'full_text']
    data: str
T = TypeVar('T')

class TranscriptionStream(ContextManager['TranscriptionStream[T]'], Iterator[T], Generic[T]):
    """Iterator wrapper that guarantees proper teardown on context exit."""
    def __init__(self, generator: Generator[T, None, None]) -> None: ...
    def __enter__(self) -> TranscriptionStream[T]: ...
    def __exit__(self, exc_type: type[BaseException] | None, exc: BaseException | None, tb: types.TracebackType | None) -> None: ...
    def __iter__(self) -> TranscriptionStream[T]: ...
    def __next__(self) -> T: ...
    def close(self) -> None: ...

class InMemoryAudioSource:
    """
    Audio source wrapping WAV bytes or a raw PCM ndarray.

    Exposes only the subset of BaseMicrophone attributes/methods that ASR uses,
    so it can be used uniformly. ``capture()`` raises ``AudioSourceExhausted``
    when the underlying buffer is drained.
    """
    sample_rate: Incomplete
    channels: Incomplete
    format: Incomplete
    format_is_packed: bool
    buffer_size: Incomplete
    def __init__(self, samples: bytes | np.ndarray) -> None: ...
    def is_started(self) -> bool: ...
    def start(self) -> None: ...
    def stop(self) -> None: ...
    def capture(self) -> np.ndarray: ...

@dataclass
class SessionInfo:
    session_id: str
    duration: int
    start_time: float
    result_queue: queue.Queue[ASREvent]
    chunk_queue: queue.Queue[bytes | object]
    cancelled: threading.Event
    reader_thread: threading.Thread | None = ...

class AutomaticSpeechRecognition:
    api_host: Incomplete
    api_port: int
    api_base_url: Incomplete
    ws_url: Incomplete
    model: Incomplete
    language: Incomplete
    def __init__(self, source: BaseMicrophone | np.ndarray | bytes | None = None, language: str | None = None) -> None:
        '''
        ASR brick that uses a local audio analytics service to decode audio streams.

        Args:
            source: Audio source for transcription. One of:
                BaseMicrophone: used as-is; the caller owns its
                    lifecycle (ASR never calls start()/stop() on it).
                bytes: treated as a WAV container and wrapped internally.
                np.ndarray: treated as raw PCM samples at 16 kHz mono
                    (dtype inferred) and wrapped internally.
                None: ASR constructs a default Microphone() and owns its
                    lifecycle (started on start(), stopped on stop()).
                Default: None.
            language (str): Language code for the ASR model (e.g. "en" for
                English). This is typically auto-detected by the model,
                but can be overridden here if needed.

        Note:
            Only one transcription can be active per instance at a time. For
            concurrent transcriptions on different mics, create multiple ASR
            instances.
        '''
    def start(self) -> None:
        """Prepare the ASR for transcription. Starts the owned mic if applicable."""
    def stop(self) -> None:
        """Stop the ASR and clean up resources. Stops the owned mic if applicable."""
    def cancel(self) -> None:
        """Cancel the active transcription session, if any."""
    def transcribe(self, duration: int = 0) -> str:
        """
        Transcribe audio from the configured source and return the final text.

        Args:
            duration (int): Maximum recording time in seconds. ``0`` means unbounded.
                Ignored for finite sources (WAV/ndarray), which are consumed
                to completion regardless. Default: ``0``.

        Returns:
            str: The transcribed text, or an empty string if no speech was detected.

        Raises:
            ASRBusyError: If this instance already has an active session.
            ASRServiceBusyError: If no more concurrent sessions are available.
            ASRUnavailableError: If the inference service is unreachable or the
                connection drops mid-session.
            RuntimeError: If the audio source has not been started.
        """
    def transcribe_stream(self, duration: int = 0) -> TranscriptionStream[ASREvent]:
        """
        Transcribe audio from the configured source and stream events.

        Args:
            duration (int): Maximum recording time in seconds. ``0`` means unbounded.
                Ignored for finite sources (WAV/ndarray). Default: ``0``.

        Yields:
            ASREvent: objects representing transcription events.

        Raises:
            ASRBusyError: If this instance already has an active session.
            ASRServiceBusyError: If no more concurrent sessions are available.
            ASRUnavailableError: If the inference service is unreachable or the
                connection drops mid-session.
            RuntimeError: If the audio source has not been started.
        """
