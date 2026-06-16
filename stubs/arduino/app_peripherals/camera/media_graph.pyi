import ctypes
from .errors import CameraOpenError as CameraOpenError
from _typeshed import Incomplete

class MediaDeviceInfo(ctypes.Structure): ...

MEDIA_IOC_DEVICE_INFO: Incomplete

def get_media_device_info(path) -> MediaDeviceInfo:
    """Return MediaDeviceInfo for a /dev/mediaX node."""
def find_camss_media_device(expected_driver: str = 'qcom-camss') -> str:
    """Return the media device driven by qcom-camss."""

class MediaEntityInfo(ctypes.Union): ...
class MediaEntityDesc(ctypes.Structure): ...
class MediaPadDesc(ctypes.Structure): ...
class MediaLinkDesc(ctypes.Structure): ...
class MediaLinksEnum(ctypes.Structure): ...

MEDIA_IOC_ENUM_ENTITIES: Incomplete
MEDIA_IOC_ENUM_LINKS: Incomplete
MEDIA_ENT_ID_FLAG_NEXT: Incomplete
MEDIA_ENT_F_CAM_SENSOR: int
MEDIA_LNK_FL_IMMUTABLE: Incomplete

def scan_sensor_i2c_addresses(media_dev: str) -> list[tuple[str, str]]:
    """
    Scan the media graph to find all sensors and their I2C addresses.
    Return a list of tuples (csiphy_name, i2c_address).
    """
def find_sensor_i2c_addr(media_dev: str, csiphy_index: int) -> str:
    """
    Traverse the media graph to find a sensor with an immutable link to the
    specified CSIPHY index.
    Return the I2C address of the found sensor.
    """
