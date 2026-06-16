import numpy as np
from _typeshed import Incomplete
from typing import Any

class Frame:
    """Represents a brightness matrix for the LED matrix.

    Internally stores a numpy array of shape (8, 13) with integer
    brightness levels in range [0, brightness_levels-1].
    """
    height: int
    width: int
    brightness_levels: Incomplete
    def __init__(self, arr: np.ndarray, brightness_levels: int = 256) -> None:
        """Create a Frame from a numpy array.

        Args:
            arr (numpy.ndarray): numpy array of shape (8, 13) with integer values
            brightness_levels (int): number of brightness levels (default 255)
        """
    def __setattr__(self, name: str, value: Any) -> None:
        """Intercept setting of certain attributes.

        Public `arr` is exposed as a read-only property; to replace the
        array please use `set_array(...)` which performs validation and assigns
        to private attribute `_arr`.
        """
    @property
    def shape(self):
        """Return the (height, width) shape of the frame as a tuple of ints."""
    @property
    def arr(self) -> np.ndarray:
        """Public read-only view of the internal array.

        Returns a numpy ndarray view with the writeable flag turned off so
        callers cannot mutate the internal storage in-place. Use
        `set_array` to replace the whole array.
        """
    @classmethod
    def from_rows(cls, rows: list[list[int]] | list[str], brightness_levels: int = 256) -> Frame:
        """Create a Frame from frontend rows.

        Args:
            rows (list[list[int]] | list[str]): Either a list of 8 lists each with 13 ints, or a list of 8
                CSV strings with 13 numeric values each.
            brightness_levels (int): Number of discrete brightness levels for the
                resulting Frame (2..256).

        Returns:
            frame: A validated `Frame` instance.

        Raises:
            ValueError: on malformed rows or out-of-range values.
        """
    def set_value(self, row: int, col: int, value: int) -> None:
        """Set a specific value in the frame array.

        Args:
            row (int): Row index (0-(height-1)).
            col (int): Column index (0-(width-1)).
            value (int): Brightness value to set (0 to brightness_levels-1).
        """
    def get_value(self, row: int, col: int) -> int:
        """Get a specific value from the frame array.

        Args:
            row (int): Row index (0-(height-1)).
            col (int): Column index (0-(width-1)).
        Returns:
            int: The brightness value at the specified position.
        """
    def set_array(self, arr: np.ndarray) -> Frame:
        """Set the internal array to a new numpy array in-place.
        Args:
            arr (numpy.ndarray): numpy array of shape (height, width) with integer values
        Returns:
            Frame: the same Frame instance after modification.
        """
    def to_board_bytes(self) -> bytes:
        """Return the byte buffer (row-major) representing this frame.

        Values are scaled to 0..255 for board consumption.

        Returns:
            Raw bytes (length height*width) suitable for the firmware.
        """
    def rescale_quantized_frame(self, scale_max: int = 255) -> np.ndarray:
        """Return a scaled numpy array with values mapped from [0, brightness_levels-1] -> [0, scale_max].

        This does not mutate self.arr; it returns a new numpy array of dtype
        uint8 suitable for sending to the board or for further formatting.
        """

class FrameDesigner:
    """Utilities to create LED matrix frames for the target board.

    FrameDesigner centralizes the LED matrix target specification and
    provides helpers to make transformations of a `Frame` instance.
    """
    width: int
    height: int
    def __init__(self) -> None:
        """Initialize the FrameDesigner instance with board defaults.

        These attributes define brightness levels used by application helpers.
        """
    def invert(self, frame: Frame) -> Frame:
        """Invert brightness values in-place on a Frame.
        Args:
            frame (Frame): Frame instance to mutate.
        Returns:
            Frame: the same Frame instance after modification.
        """
    def invert_not_null(self, frame: Frame) -> Frame:
        """Invert non-zero brightness values in-place on a Frame.
        Args:
            frame (Frame): Frame instance to mutate.
        Returns:
            Frame: the same Frame instance after modification.
        """
    def rotate180(self, frame: Frame) -> Frame:
        """Rotate a Frame by 180 degrees in-place.
        Args:
            frame (Frame): Frame instance to mutate.
        Returns:
            Frame: the same Frame instance after modification.
        """
    def flip_horizontally(self, frame: Frame) -> Frame:
        """Flip a Frame horizontally in-place.
        Args:
            frame (Frame): Frame instance to mutate.
        Returns:
            Frame: the same Frame instance after modification.
        """
    def flip_vertically(self, frame: Frame) -> Frame:
        """Flip a Frame vertically in-place.
        Args:
            frame (Frame): Frame instance to mutate.
        Returns:
            Frame: the same Frame instance after modification.
        """
