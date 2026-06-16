from .google import GoogleSpeech as GoogleSpeech
from .openai import OpenAITranscribe as OpenAITranscribe
from .types import ASRProvider as ASRProvider, ASRProviderError as ASRProviderError, ASRProviderEvent as ASRProviderEvent
from _typeshed import Incomplete
from enum import Enum

__all__ = ['OpenAITranscribe', 'GoogleSpeech', 'ASRProvider', 'ASRProviderEvent', 'ASRProviderError', 'CloudProvider', 'DEFAULT_PROVIDER', 'provider_factory']

class CloudProvider(str, Enum):
    OPENAI_TRANSCRIBE = 'openai-transcribe'
    GOOGLE_SPEECH = 'google-speech'

DEFAULT_PROVIDER: Incomplete

def provider_factory(api_key: str, language: str, sample_rate: int, name: CloudProvider = ...) -> ASRProvider:
    """Return the ASR cloud provider implementation."""
