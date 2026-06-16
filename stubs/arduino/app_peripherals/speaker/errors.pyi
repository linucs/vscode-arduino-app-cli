class SpeakerError(Exception):
    """Base exception for Speaker-related errors."""
class SpeakerOpenError(SpeakerError):
    """Exception raised when the speaker cannot be opened."""
class SpeakerWriteError(SpeakerError):
    """Exception raised when writing to speaker fails."""
class SpeakerConfigError(SpeakerError):
    """Exception raised when speaker configuration is invalid."""
