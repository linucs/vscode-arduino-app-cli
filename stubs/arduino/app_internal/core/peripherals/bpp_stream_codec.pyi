from .bpp_codec import BPPCodec as BPPCodec
from _typeshed import Incomplete
from typing import Iterator

MAGIC: int
HEADER_FORMAT: str
HEADER_SIZE: Incomplete

class BPPStreamCodec:
    """
    Wraps a BPPCodec to provide support for stream-based protocols (e.g. TCP,
    BLE, UART).

    The binary format is as follows:

    [Magic(1)] [Length(4)] [HeaderCRC(1)] [BPP Packet]

    - Magic Byte: 0xAA, marks the start of a BPP frame.
    - Length: 4-byte big-endian unsigned int indicating the length of the BPP packet.
    - HeaderCRC: Simple checksum over the Length and Magic byte for header integrity.
    - BPP Packet: The actual BPP-encoded packet as per BPPCodec.
    """
    codec: Incomplete
    def __init__(self, codec: BPPCodec) -> None: ...
    def encode(self, data: bytes) -> bytes: ...
    def decode(self, chunk: bytes = b'') -> Iterator[bytes]:
        """
        Ingests a stream chunk and yields all fully decoded BPP payloads found.

        Yields:
            Decoded payloads (bytes)
        """
