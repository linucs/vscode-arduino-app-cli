from .types import ASRProviderEvent
from _typeshed import Incomplete

__all__ = ['GoogleSpeech']

class GoogleSpeech:
    """
    Google ASR cloud provider implementation.

    It uses google cloud speech package to connect to Google Speech-to-Text API
    for streaming transcription.
    For English locales it uses the default streaming model. For non-English
    locales the standard model segments poorly, so `latest_short` is used to
    get faster segmentation even though it emits a single utterance; when that
    happens the stream is restarted transparently while preserving queued
    audio so callers keep a continuous feed of events.
    """
    provider_name: str
    partial_mode: str
    GOOGLE_LANG_MAP: Incomplete
    DEFAULT_LANGUAGE: str
    def __init__(self, api_key: str, language: str = ..., sample_rate: int = 16000) -> None: ...
    def start(self) -> None:
        """Start the ASR session."""
    def send_audio(self, pcm_chunk: bytes) -> None: ...
    def recv(self) -> ASRProviderEvent | None: ...
    def stop(self) -> None: ...
