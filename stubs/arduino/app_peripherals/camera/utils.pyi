from .errors import CameraOpenError as CameraOpenError

def nth_plugged_camera(idx: int) -> str:
    """
    Find the n-th available physically connected camera.
    The precedence is USB cameras first, then CSI cameras, if supported
    by the current platform.

    Args:
        idx (int): Index of the camera to select (0-based).

    Returns:
        str | int: Identifier of the n-th available camera

    Raises:
        CameraOpenError: If no cameras are found or index is out of range
    """
def resolve_camera_name(i2c_addr: str) -> str:
    """
    Find the camera name corresponding to the given I2C address.

    Args:
        i2c_addr (str): I2C address of the camera.

    Returns:
        str: Camera name corresponding to the I2C address.

    Raises:
        CameraOpenError: If no camera matches the given I2C address.
    """
