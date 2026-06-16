from .types import ASRProviderEvent
from _typeshed import Incomplete

__all__ = ['OpenAITranscribe']

class OpenAITranscribe:
    '''
    OpenAI ASR cloud provider implementation.
    It leverages the Realtime API to enable streaming transcription powered by a GPT-based model.
    Audio is transmitted and received over WebSockets, while voice activity detection (VAD) server-side
    is used to segment utterances.
    If custom VAD behavior is desired, the VoiceActivityDetector class can be used client-side to
    trigger commits based on local audio analysis. In that case, track the audio with the vad process_chunk method and
    register the vad commit() method to send a `{"type": "input_audio_buffer.commit"}` message to the server.
    '''
    provider_name: str
    partial_mode: str
    REALTIME_MODEL: str
    TRANSCRIPTION_MODEL: str
    BASE_URL: str
    IGNORED_COMMIT_CODES: Incomplete
    VAD_MIN_BUFFER_MS: float
    DEFAULT_LANGUAGE: str
    def __init__(self, api_key: str, language: str = ..., sample_rate: int = 16000) -> None: ...
    def start(self) -> None:
        """Start the ASR session."""
    def recv(self) -> ASRProviderEvent | None: ...
    def send_audio(self, pcm_chunk: bytes) -> None: ...
    def stop(self) -> None: ...
