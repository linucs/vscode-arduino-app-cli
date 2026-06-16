import numpy as np
from .base_microphone import BaseMicrophone as BaseMicrophone, FormatPacked as FormatPacked, FormatPlain as FormatPlain

class Microphone:
    """
    Unified Microphone class that can be configured for different microphone types.

    This class serves as both a factory and a wrapper, automatically creating
    the appropriate microphone implementation based on the provided configuration.

    Supports:
        - ALSA Microphones (local microphones connected to the system via ALSA)
        - WebSocket Microphones (input audio streams via WebSocket client)

    Note: constructor arguments (except those in signature) must be provided in
    keyword format to forward them correctly to the specific microphone implementations.
    Refer to the documentation of each microphone type for available parameters.
    """
    USB_MIC_1: str
    USB_MIC_2: str
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
    def __new__(cls, device: str | int = ..., sample_rate: int = ..., channels: int = ..., format: FormatPlain | FormatPacked = ..., buffer_size: int = ..., **kwargs) -> BaseMicrophone:
        '''
        Create a microphone instance based on the device type.

        Args:
            device (Union[str, int]): Microphone device identifier. Supports:
                - int | str: ALSA device ordinal index (e.g., 0, 1, "0", "1", ...)
                - str: ALSA device name (e.g., "plughw:CARD=MyCard,DEV=0", "hw:0,0", "CARD=MyCard,DEV=0")
                - str: ALSA device file path (e.g., "/dev/snd/by-id/usb-My-Device-00")
                - str: Microphone.USB_MIC_x macros
                - str: WebSocket URL for audio streams (e.g., "ws://0.0.0.0:8080")
                Default: USB_MIC_1 - First USB microphone.
            sample_rate (int): Sample rate in Hz. Default: 16000
            channels (int): Number of audio channels. Default: 1
            format (FormatPlain | FormatPacked): Audio format as one of:
                - Type classes: np.int16, np.float32, np.uint8
                - dtype objects: np.dtype(\'<i2\'), np.dtype(\'>f4\')
                - Strings: \'int16\', \'<i2\', \'>f4\', \'float32\'
                - Tuple of (format, is_packed): to specify if the format is packed (e.g. 24-bit audio)
                Default: np.int16 - 16-bit signed platform-endian.
            buffer_size (int): Size of the audio buffer. Default: 1024.
            **kwargs: Microphone-specific configuration parameters grouped by type:
                ALSA Microphone Parameters:
                    shared (bool): Whether the microphone can be used by multiple applications
                        simultaneously. Default: True.
                    auto_reconnect (bool): Whether to automatically attempt to reconnect
                        if the microphone connection is lost. Default: True.
                WebSocket Microphone Parameters:
                    port (int): WebSocket server port. Default: 8080
                    timeout (float): Connection timeout in seconds. Default: 3.0
                    certs_dir_path (str): Path to the directory containing TLS certificates.
                    use_tls (bool): Enable TLS for secure connections. If True, \'encrypt\' will
                        be ignored. Use this for transport-level security with clients that can
                        accept self-signed certificates or when supplying your own certificates.
                    secret (str | None): Pre-shared secret key. None disables security.
                        Default: None.
                    encrypt (bool): Enable encryption. Requires a secret, raises
                        RuntimeError otherwise. Default: False.
                    auto_reconnect (bool): Whether to automatically attempt to reconnect
                        if the microphone connection is lost. Default: True.

        Returns:
            BaseMicrophone: Appropriate microphone implementation instance

        Raises:
            MicrophoneConfigError: If device type is not supported or parameters are invalid

        Examples:
            ALSA Microphone:

            ```python
            microphone = Microphone(sample_rate=16000, channels=1)  # First USB microphone
            microphone = Microphone(USB_MIC_1, sample_rate=16000, channels=1)  # Equivalent to above
            microphone = Microphone(1)  # Second microphone
            microphone = Microphone("CARD=MyCard,DEV=0", format="S16_LE")
            microphone = Microphone("plughw:CARD=MyCard,DEV=0")
            microphone = Microphone("hw:0,0")
            microphone = Microphone("/dev/snd/by-id/usb-My-Device-00")  # Using device file path
            ```

            WebSocket Microphone:

            ```python
            microphone = Microphone("ws://0.0.0.0:8080", sample_rate=48000)
            microphone = Microphone("ws://0.0.0.0:8080", secret="topsecret", encrypt=True)
            ```
        '''
    @staticmethod
    def record_pcm(duration: float, sample_rate: int, channels: int, format: FormatPlain | FormatPacked, device: str | int = ...) -> np.ndarray:
        '''
        Record audio for a specified duration and return as raw PCM format.

        Args:
            duration (float): Recording duration in seconds.
            sample_rate (int): Sample rate in Hz.
            channels (int): Number of audio channels.
            format (FormatPlain | FormatPacked): Audio format as one of:
                - Type classes: np.int16, np.float32, np.uint8
                - dtype objects: np.dtype(\'<i2\'), np.dtype(\'>f4\')
                - Strings: \'int16\', \'<i2\', \'>f4\', \'float32\'
                - Tuple of (format, is_packed): to specify if the format is packed (e.g. 24-bit audio)
            device (Union[str, int]): Microphone device identifier. Supports:
                - int | str: ALSA device ordinal index (e.g., 0, 1, "0", "1", ...)
                - str: ALSA device name (e.g., "plughw:CARD=MyCard,DEV=0", "hw:0,0", "CARD=MyCard,DEV=0")
                - str: ALSA device file path (e.g., "/dev/snd/by-id/usb-My-Device-00")
                - str: Microphone.USB_MIC_x macros
                - str: WebSocket URL for audio streams (e.g., "ws://0.0.0.0:8080")
                Default: USB_MIC_1 - First USB microphone.

        Returns:
            np.ndarray: Raw audio data in raw PCM format.

        Raises:
            MicrophoneOpenError: If microphone can\'t be opened.
            MicrophoneReadError: If no audio is available after multiple attempts.
            ValueError: If duration is not > 0.
            Exception: If the underlying implementation fails to read a frame.
        '''
    @staticmethod
    def record_wav(duration: float, sample_rate: int, channels: int, format: FormatPlain | FormatPacked, device: str | int = ...) -> np.ndarray:
        '''
        Record audio for a specified duration and return as WAV format.
        Note: Only uncompressed PCM WAV recordings are supported.

        Args:
            duration (float): Recording duration in seconds.
            sample_rate (int): Sample rate in Hz.
            channels (int): Number of audio channels.
            format (FormatPlain | FormatPacked): Audio format as one of:
                - Type classes: np.int16, np.float32, np.uint8
                - dtype objects: np.dtype(\'<i2\'), np.dtype(\'>f4\')
                - Strings: \'int16\', \'<i2\', \'>f4\', \'float32\'
                - Tuple of (format, is_packed): to specify if the format is packed (e.g. 24-bit audio)
            device (Union[str, int], optional): Microphone device identifier. Supports:
                - int | str: ALSA device ordinal index (e.g., 0, 1, "0", "1", ...)
                - str: ALSA device name (e.g., "plughw:CARD=MyCard,DEV=0", "hw:0,0", "CARD=MyCard,DEV=0")
                - str: ALSA device file path (e.g., "/dev/snd/by-id/usb-My-Device-00")
                - str: Microphone.USB_MIC_x macros
                - str: WebSocket URL for audio streams (e.g., "ws://0.0.0.0:8080")
                Default: USB_MIC_1 - First USB microphone.

        Returns:
            np.ndarray: Raw audio data in WAV format as numpy array.

        Raises:
            MicrophoneOpenError: If microphone can\'t be opened.
            MicrophoneReadError: If no audio is available after multiple attempts.
            ValueError: If duration is not > 0.
            Exception: If the underlying implementation fails to read a frame.
        '''
