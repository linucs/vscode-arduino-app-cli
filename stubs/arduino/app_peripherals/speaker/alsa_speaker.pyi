from .base_speaker import BaseSpeaker as BaseSpeaker, FormatPacked as FormatPacked, FormatPlain as FormatPlain
from .errors import SpeakerConfigError as SpeakerConfigError, SpeakerOpenError as SpeakerOpenError, SpeakerWriteError as SpeakerWriteError
from .speaker import Speaker as Speaker
from _typeshed import Incomplete
from arduino.app_utils.logger import Logger as Logger

logger: Incomplete

class ALSASpeaker(BaseSpeaker):
    """
    ALSA (Advanced Linux Sound Architecture) speaker implementation.

    This class handles local audio playback devices on Linux systems using ALSA.
    """
    device_stable_ref: Incomplete
    name: Incomplete
    shared: Incomplete
    logger: Incomplete
    def __init__(self, device: str | int = ..., sample_rate: int = ..., channels: int = ..., format: FormatPlain | FormatPacked = ..., buffer_size: int = ..., shared: bool = True, auto_reconnect: bool = True) -> None:
        '''
        Initialize ALSA speaker.

        Args:
            device (Union[str, int]): ALSA device identifier. Can be:
                - int | str: device ordinal index (e.g., 0, 1, "0", "1", ...)
                - str: device name (e.g., "plughw:CARD=MyCard,DEV=0", "hw:0,0", "CARD=MyCard,DEV=0")
                - str: device file path (e.g., "/dev/snd/by-id/usb-My-Device-00")
                - str: Speaker.USB_SPEAKER_x macros
                Default: Speaker.USB_SPEAKER_1 - First USB speaker available.
            sample_rate (int): Sample rate in Hz. Default: 16000.
            channels (int): Number of audio channels. Default: 1 (mono).
            format (FormatPlain | FormatPacked): Audio format as one of:
                - Type classes: np.int16, np.float32, np.uint8
                - dtype objects: np.dtype(\'<i2\'), np.dtype(\'>f4\')
                - Strings: \'int16\', \'<i2\', \'>f4\', \'float32\'
                - Tuple of (format, is_packed): to specify if the format is packed (e.g. 24-bit audio)
                Default: np.int16 - 16-bit signed platform-endian.
            buffer_size (int): Size of the audio buffer that will be used as ALSA periodsize
                parameter. Low values increase CPU usage but reduce latency. Default: 1024.
            shared (bool): ALSA device sharing mode.
                - False: Opens the device in exclusive mode to provide lowest latency
                    but another application will fail when this instance is using the device.
                - True: Opens the device in shared mode to allow other applications to use
                    it at the same time but introduces higher latency. Will fail when another
                    instance is already using the device in exclusive mode.
                Default: True.
            auto_reconnect (bool): Enable automatic reconnection on failure.
                Default: True.

            Note: When shared=True, buffer size is auto-negotiated due to
                ALSA limitations to reach 125ms of latency.

        Raises:
            SpeakerConfigError: If the format is not supported.
        '''
    @property
    def alsa_format_idx(self) -> int:
        """Get the ALSA format index corresponding to the current numpy dtype format."""
    @property
    def alsa_format_name(self) -> str:
        """Get the ALSA format string corresponding to the current numpy dtype format."""
    @staticmethod
    def list_devices() -> list:
        """
        Return a list of available ALSA speakers (plughw only).

        Returns:
            list: List of speakers in ALSA device name format.
        """
    @staticmethod
    def list_usb_devices() -> list:
        """
        Return a list of available USB ALSA speakers (plughw only).

        Returns:
            list: List of USB speakers in ALSA device name format.
        """
