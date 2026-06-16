from dataclasses import dataclass
from typing import Callable

__all__ = ['ENERGY_THRESHOLD', 'SILENCE_MS', 'MAX_BUFFER_MS', 'VADState', 'VoiceActivityDetector', 'chunk_duration_ms']

ENERGY_THRESHOLD: float
SILENCE_MS: float
MAX_BUFFER_MS: float

@dataclass
class VADState:
    buffered_ms: float = ...
    silence_ms: float = ...
    speaking: bool = ...

class VoiceActivityDetector:
    """
    This class analyzes incoming PCM16 audio chunks by estimating their signal
    energy to determine whether speech is present. Chunks with energy above the
    configured threshold are classified as speech, while lower-energy chunks
    contribute to silence accumulation.

    Audio duration is buffered while speech is active and a commit callback is
    triggered when one of the following conditions is met:

    - A period of silence longer than the configured silence threshold occurs
    after speech has started.
    - The maximum allowed buffered audio duration is reached.

    The detector is stateful and must be fed sequential audio chunks from a
    continuous audio stream.

    Args:
        commit_callback (Callable[[], None]):
            Function invoked when the buffered audio should be committed.

        min_buffer_ms (float):
            Minimum amount of buffered audio (in milliseconds) required to
            trigger a commit. Shorter segments are discarded.

        energy_threshold (float, optional):
            Energy threshold used to classify a chunk as speech.
            Higher values make the detector less sensitive to quiet speech.
            Defaults to `ENERGY_THRESHOLD`.

        silence_ms (float, optional):
            Amount of consecutive silence (in milliseconds) required to
            consider speech ended and trigger a commit.
            Defaults to `SILENCE_MS`.

        max_buffer_ms (float, optional):
            Maximum amount of audio (in milliseconds) that can be buffered
            before forcing a commit, even if speech has not ended.
            Defaults to `MAX_BUFFER_MS`.
    """
    def __init__(self, commit_callback: Callable[[], None], min_buffer_ms: float, energy_threshold: float = ..., silence_ms: float = ..., max_buffer_ms: float = ...) -> None: ...
    def process_chunk(self, pcm_chunk: bytes, sample_rate: int) -> None:
        """Update VAD state using raw PCM16 bytes and commit buffered audio when thresholds are met."""
    def commit_buffer(self) -> None: ...
    def flush(self) -> None: ...

def chunk_duration_ms(pcm_chunk: bytes, sample_rate: int) -> float: ...
