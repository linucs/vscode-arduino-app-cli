import numpy as np
from .base_speaker import BaseSpeaker as BaseSpeaker, FormatPacked as FormatPacked, FormatPlain as FormatPlain

class Speaker:
    """
    Unified Speaker class that can be configured for different speaker types.

    This class serves as both a factory and a wrapper, automatically creating
    the appropriate speaker implementation based on the provided configuration.

    Supports:
        - ALSA Speakers (local speakers connected to the system via ALSA)

    Note: constructor arguments (except those in signature) must be provided in
    keyword format to forward them correctly to the specific speaker implementations.
    Refer to the documentation of each speaker type for available parameters.
    """
    USB_SPEAKER_1: str
    USB_SPEAKER_2: str
    RATE_8K: int
    RATE_16K: int
    RATE_32K: int
    RATE_44K: int
    RATE_48K: int
    CHANNELS_MONO: int
    CHANNELS_STEREO: int
    BUFFER_SIZE_REALTIME: int
    BUFFER_SIZE_BALANCED: int
    BUFFER_SIZE_SAFE: int
    def __new__(cls, device: str | int = ..., sample_rate: int = ..., channels: int = ..., format: FormatPlain | FormatPacked = ..., buffer_size: int = ..., **kwargs) -> BaseSpeaker:
        '''
        Create a speaker instance based on the device type.

        Args:
            device (Union[str, int]): Speaker device identifier. Supports:
                - int | str: ALSA device ordinal index (e.g., 0, 1, "0", "1", ...)
                - str: ALSA device name (e.g., "plughw:CARD=MyCard,DEV=0", "hw:0,0", "CARD=MyCard,DEV=0")
                - str: ALSA device file path (e.g., "/dev/snd/by-id/usb-My-Device-00")
                - str: Speaker.USB_SPEAKER_x macros
            sample_rate (int): Sample rate in Hz. Default: 16000.
            channels (int): Number of audio channels. Default: 1.
            format (FormatPlain | FormatPacked): Audio format as one of:
                - Type classes: np.int16, np.float32, np.uint8
                - dtype objects: np.dtype(\'<i2\'), np.dtype(\'>f4\')
                - Strings: \'int16\', \'<i2\', \'>f4\', \'float32\'
                - Tuple of (format, is_packed): to specify if the format is packed (e.g. 24-bit audio)
                Default: np.int16 - 16-bit signed platform-endian.
            buffer_size (int): Size of the audio buffer. Default: 1024.
            **kwargs: Speaker-specific configuration parameters grouped by type:

                ALSA Speaker Parameters:
                    shared (bool): Whether the speaker can be used by multiple applications
                        simultaneously. Default: True.
                    auto_reconnect (bool): Whether to automatically attempt to reconnect
                        if the speaker connection is lost. Default: True.

        Returns:
            BaseSpeaker: Appropriate speaker implementation instance

        Raises:
            SpeakerConfigError: If device type is not supported or parameters are invalid

        Examples:
            ALSA Speaker:

            ```python
            speaker = Speaker(sample_rate=16000, channels=1)  # First USB speaker
            speaker = Speaker(USB_SPEAKER_1, sample_rate=16000, channels=1)  # Equivalent to above
            speaker = Speaker(1)  # Second speaker
            speaker = Speaker("CARD=USB,DEV=0", format="S16_LE")
            speaker = Speaker("plughw:CARD=USB,DEV=0")
            speaker = Speaker("hw:0,0", buffer_size=2048)
            speaker = Speaker("/dev/snd/by-id/usb-My-Device-00")  # Using device file path
            ```
        '''
    @staticmethod
    def play_pcm(pcm_audio: np.ndarray, sample_rate: int, channels: int, format: FormatPlain | FormatPacked, device: str | int = ...):
        '''
        Play raw PCM audio data.

        Args:
            pcm_audio (np.ndarray): Raw PCM audio data in ALSA PCM format.
            sample_rate (int): Sample rate in Hz.
            channels (int): Number of audio channels.
            format (FormatPlain | FormatPacked): Audio format as one of:
                - Type classes: np.int16, np.float32, np.uint8
                - dtype objects: np.dtype(\'<i2\'), np.dtype(\'>f4\')
                - Strings: \'int16\', \'<i2\', \'>f4\', \'float32\'
                - Tuple of (format, is_packed): to specify if the format is packed (e.g. 24-bit audio)
            device (Union[str, int], optional): Speaker device identifier. Supports:
                - int | str: ALSA device ordinal index (e.g., 0, 1, "0", "1", ...)
                - str: ALSA device name (e.g., "plughw:CARD=MyCard,DEV=0", "hw:0,0", "CARD=MyCard,DEV=0")
                - str: ALSA device file path (e.g., "/dev/snd/by-id/usb-My-Device-00")
                - str: Speaker.USB_SPEAKER_x macros
                Default: Speaker.USB_SPEAKER_1 - First USB speaker available.

        Raises:
            SpeakerOpenError: If speaker can\'t be opened.
            SpeakerWriteError: If speaker is not started.
            ValueError: If pcm_audio is empty or invalid.
            Exception: If the underlying implementation fails to write a frame.
        '''
    @staticmethod
    def play_wav(wav_audio: np.ndarray, device: str | int = ...):
        '''
        Play audio from WAV format data.
        Note: Only uncompressed PCM WAV files are supported.

        Args:
            wav_audio (np.ndarray): WAV format audio data (including header).
            device (Union[str, int], optional): Speaker device identifier. Supports:
                - int | str: ALSA device ordinal index (e.g., 0, 1, "0", "1", ...)
                - str: ALSA device name (e.g., "plughw:CARD=MyCard,DEV=0", "hw:0,0", "CARD=MyCard,DEV=0")
                - str: ALSA device file path (e.g., "/dev/snd/by-id/usb-My-Device-00")
                - str: Speaker.USB_SPEAKER_x macros
                Default: Speaker.USB_SPEAKER_1 - First USB speaker available.

        Raises:
            SpeakerOpenError: If speaker can\'t be opened.
            SpeakerWriteError: If speaker is not started.
            ValueError: If wav_audio is empty or invalid.
            Exception: If the underlying implementation fails to write a frame.
        '''
