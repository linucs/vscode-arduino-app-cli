from _typeshed import Incomplete
from arduino.app_utils.logger import Logger as Logger

logger: Incomplete
BPP_VERSION: int
MODE_NONE: int
MODE_SIGN: int
MODE_ENC: int
HEADER_FORMAT: str
HEADER_SIZE: Incomplete
WINDOW_US: int

class ReplayProtection:
    """
    Manages the sliding window replay protection and the temporary cache storing
    the IVs already seen within the validity window.
    """
    window_us: Incomplete
    cache: dict[bytes, int]
    def __init__(self, window_us: int = ...) -> None: ...
    def check_and_update(self, iv: bytes, timestamp_us: int) -> bool:
        """
        Determines if the message is valid by assessing replay attack conditions:
        timestamp out of validity window and IV reuse.
        """

class BPPCodec:
    """
    Binary Peripheral Protocol (BPP) Codec.
    Implements a secure container format for peripherals and allows to encode and
    decode payloads.
    This codec is intended to be used with message-based protocols, i.e. with builtin
    message boundaries (e.g., WebSocket). If used with stream-based protocols (e.g.,
    TCP, BLE, UART), it must be wrapped in BPPStreamCodec.

    The protocol supports three security modes:
    - Mode 0: No Security;
    - Mode 1: HMAC-SHA256 Signing, useful for authentication and data integrity;
    - Mode 2: ChaCha20-Poly1305 Encryption and Signing, providing confidentiality,
        authentication and data integrity.

    The binary format is as follows:

    [Version (1)] [Mode (1)] [Timestamp (8)] [Random (4)] [Payload (Var)] [AuthTag/Sig (16/32)]

    - Version: Protocol version (currently 0x01).
    - Mode: Security mode (0x00: None, 0x01: HMAC-SHA256, 0x02: ChaCha20-Poly1305).
    - Timestamp: Microsecond-precision timestamp (Unix epoch).
    - Random: 32-bit random value for uniqueness.
    - Payload: Actual data being transmitted.
    - AuthTag/Sig: HMAC signature (32 bytes for Mode 1) or AuthTag (16 bytes for Mode 2).

    Text-safe encoding/decoding via Base64URL are also provided.
    """
    secret: Incomplete
    enable_encryption: Incomplete
    cc_cipher: Incomplete
    replay_protection: Incomplete
    def __init__(self, secret: str = '', enable_encryption: bool = False) -> None:
        """
        Initialize codec.

        Args:
            secret: Pre-shared secret. Default: empty (no security).
            enable_encryption: If True, uses ChaCha20-Poly1305. If False, uses HMAC-SHA256 if
                secret is provided. Default: False.
        """
    def encode(self, data: bytes) -> bytes:
        """
        Packs data into a BPP message and returns its bytes.

        Args:
            data: The payload to encode.
        Returns:
            The complete BPP message (bytes).
        """
    def decode(self, message: bytes) -> bytes | None:
        """
        Unpacks a BPP message and returns its payload.

        Args:
            message: The complete BPP message to decode.
        Returns:
            The decoded payload (bytes) if valid, else None.
        """
    def encode_text(self, data: bytes) -> str:
        """
        Encodes a text-safe BPP packet to a Base64URL string.
        """
    def decode_text(self, b64_str: str) -> bytes | None:
        """
        Decodes a text-safe BPP packet from a Base64URL string.
        """
