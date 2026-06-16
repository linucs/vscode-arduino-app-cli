from .providers import ASRProvider as ASRProvider, CloudProvider as CloudProvider, DEFAULT_PROVIDER as DEFAULT_PROVIDER, provider_factory as provider_factory
from .providers.types import ASRProviderError as ASRProviderError, ASRProviderEvent as ASRProviderEvent
from .types import ASREvent as ASREvent, ASREventType as ASREventType, ASREventTypeValues as ASREventTypeValues
from _typeshed import Incomplete
from arduino.app_peripherals.microphone import Microphone as Microphone
from arduino.app_peripherals.microphone.base_microphone import BaseMicrophone as BaseMicrophone
from arduino.app_utils import Logger as Logger, brick as brick
from contextlib import contextmanager
from typing import Iterator

logger: Incomplete
DEFAULT_LANGUAGE: str

class TranscriptionTimeoutError(TimeoutError): ...
class TranscriptionStreamError(RuntimeError): ...

class CloudASR:
    """
    Cloud-based speech-to-text with pluggable cloud providers.
    It captures audio from a microphone and streams it to the selected cloud ASR provider for transcription.
    The recognized text is yielded as events in real-time.
    """
    silence_timeout: Incomplete
    def __init__(self, api_key: str = ..., provider: CloudProvider = ..., mic: BaseMicrophone | None = None, language: str = ..., silence_timeout: float = 10.0) -> None: ...
    def start(self) -> None:
        """Start the ASR service by initializing the microphone."""
    def stop(self) -> None:
        """
        Stop the ASR service: signal in-flight transcriptions and release
        the mic if owned.
        """
    def transcribe(self, duration: float = 60.0) -> str:
        """
        Returns the first utterance transcribed from speech to text.

        Args:
            duration (float): Max seconds for the transcription session.

        Returns:
            str: The transcribed text.
        """
    @contextmanager
    def transcribe_stream(self, duration: float = 60.0) -> Iterator[Iterator[ASREvent]]:
        """
        Perform continuous speech-to-text recognition.

        Args:
            duration (float): Max seconds for the transcription session.

        Returns:
            Iterator[ASREvent]: Generator yielding transcription events.
        """
