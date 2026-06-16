from .base_microphone import BaseMicrophone as BaseMicrophone, FormatPacked as FormatPacked, FormatPlain as FormatPlain
from .errors import MicrophoneConfigError as MicrophoneConfigError, MicrophoneOpenError as MicrophoneOpenError
from .microphone import Microphone as Microphone
from _typeshed import Incomplete
from arduino.app_internal.core.peripherals import BPPCodec as BPPCodec
from arduino.app_utils import Logger as Logger

logger: Incomplete

class WebSocketMicrophone(BaseMicrophone):
    '''
    WebSocket Microphone implementation that hosts a WebSocket server.

    This microphone exposes a WebSocket server that receives audio chunks from
    a connected client. Only one client can be connected at a time.

    The client must encode the audio data in PCM format and must respect the
    sample rate, channels, format, and chunk size specified during initialization.

    Communication uses the BPP (Binary Peripheral Protocol) in three security modes:
    - Security disabled (secret=None) - BPP with no authentication
    - Authenticated (secret + encrypt=False) - BPP with HMAC-SHA256
    - Authenticated + Encrypted (secret + encrypt=True) - BPP with ChaCha20-Poly1305

    By default, all modes use BPP framing. When security is disabled (secret=None),
    clients can opt out of BPP by connecting with the "raw=true" URL query parameter,
    allowing them to send raw PCM bytes directly without BPP wrapping. This parameter
    is silently ignored when security is enabled.

    When connecting, clients can specify a "client_name" parameter in the URL query string
    to identify themselves. This name will be sanitized to allow only alphanumeric chars,
    whitespace, hyphens, and underscores, and limit its length to 64 characters.
    '''
    codec: Incomplete
    secret: Incomplete
    encrypt: Incomplete
    logger: Incomplete
    name: Incomplete
    use_tls: Incomplete
    protocol: Incomplete
    ip: Incomplete
    port: Incomplete
    timeout: Incomplete
    def __init__(self, port: int = 8080, timeout: int = 3, certs_dir_path: str = '/app/certs', use_tls: bool = False, secret: str | None = None, encrypt: bool = False, sample_rate: int = ..., channels: int = ..., format: FormatPlain | FormatPacked = ..., buffer_size: int = ..., auto_reconnect: bool = True) -> None:
        '''
        Initialize WebSocket microphone server.

        Args:
            port (int): Port to bind the server to. Default: 8080.
            timeout (int): Connection timeout in seconds. Default: 3.
            certs_dir_path (str): Path to the directory containing TLS certificates.
                Default: "/app/certs".
            use_tls (bool): Enable TLS for secure connections. If True, \'encrypt\' will
                be ignored. Use this for transport-level security with clients that can
                accept self-signed certificates or when supplying your own certificates.
                Default: False.
            secret (str | None): Pre-shared secret key used for HMAC-SHA256
                authentication, or to derive the ChaCha20-Poly1305 key when
                encrypt is True. None disables security. Default: None.
            encrypt (bool): Enable ChaCha20-Poly1305 encryption. Requires a
                non-None secret; raises RuntimeError otherwise. Default: False.
            sample_rate (int): Sample rate in Hz. Default: 16000.
            channels (int): Number of audio channels. Default: Microphone.CHANNELS_MONO - 1.
            format (FormatPlain | FormatPacked): Audio format as one of:
                - Type classes: np.int16, np.float32, np.uint8
                - dtype objects: np.dtype(\'<i2\'), np.dtype(\'>f4\')
                - Strings: \'int16\', \'<i2\', \'>f4\', \'float32\'
                - Tuple of (format, is_packed): to specify if the format is packed (e.g. 24-bit audio)
                Default: np.int16 - 16-bit signed platform-endian.
            buffer_size (int): Number of frames per buffer (default: 1024). This parameter is advisory,
                it\'s sent to clients to suggest an optimal buffer size but clients may ignore it.
                Default: Microphone.BUFFER_SIZE_BALANCED - 1024.
            auto_reconnect (bool): Enable automatic reconnection on failure.
        '''
    @property
    def url(self) -> str:
        """Return the WebSocket server address."""
    @property
    def security_mode(self) -> str:
        """Return current security mode for logging/debugging."""
