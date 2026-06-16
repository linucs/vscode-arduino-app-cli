from _typeshed import Incomplete
from dataclasses import dataclass
from typing import Protocol

ASRProviderEventType: Incomplete

@dataclass(frozen=True)
class ASRProviderEvent:
    type: ASRProviderEventType
    data: str | None = ...

class ASRProviderError(Exception):
    """Base class for ASR-related errors."""

class ASRProvider(Protocol):
    """Minimal interface for realtime ASR cloud providers."""
    @property
    def provider_name(self) -> str: ...
    @property
    def partial_mode(self) -> str: ...
    def start(self) -> None: ...
    def send_audio(self, pcm_chunk: bytes) -> None: ...
    def recv(self) -> ASRProviderEvent | None: ...
    def stop(self) -> None: ...
