class MicrophoneError(Exception):
    """Base exception for microphone-related errors."""
class MicrophoneOpenError(MicrophoneError):
    """Exception raised when the microphone cannot be opened."""
class MicrophoneReadError(MicrophoneError):
    """Exception raised when reading from microphone fails."""
class MicrophoneConfigError(MicrophoneError):
    """Exception raised when microphone configuration is invalid."""
