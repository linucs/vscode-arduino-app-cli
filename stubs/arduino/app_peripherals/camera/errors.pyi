class CameraError(Exception):
    """Base exception for camera-related errors."""
class CameraOpenError(CameraError):
    """Exception raised when the camera cannot be opened."""
class CameraReadError(CameraError):
    """Exception raised when reading from camera fails."""
class CameraConfigError(CameraError):
    """Exception raised when camera configuration is invalid."""
class CameraTransformError(CameraError):
    """Exception raised when frame transformation fails."""
