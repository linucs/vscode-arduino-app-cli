import numpy as np
from _typeshed import Incomplete

class SlidingWindowBuffer:
    """A sliding window buffer for managing generic streaming data.
    This buffer allows a single producer to push data and a single consumer to pull that data in a sliding window
    manner. The data type (dtype) and item shape are inferred from the first array pushed to the buffer.

    By providing a slide_amount < window_size, the buffer implements a sliding window where older data is
    repeated but newer data (with slide_amount length) is always available.
    By providing a slide_amount == window_size, the buffer implements a tumbling window where older data
    is never repeated and only new data (with window_size length) is always available.
    """
    window_size: Incomplete
    slide_amount: Incomplete
    capacity: Incomplete
    def __init__(self, window_size: int, slide_amount: int, capacity: int = None) -> None:
        """Initializes the sliding window buffer.

        Args:
            window_size (int): The size of the sliding window.
            slide_amount (int): The amount by which the window slides each time data is pulled.
            capacity (int, optional): The maximum number of items the buffer can hold. If None, defaults to 2 * window_size.
            dtype (np.dtype, optional): The data type of the buffer. Defaults to np.int16.

        Raises:
            ValueError: If window_size, slide_amount or capacity have incorrect values.
            TypeError: If dtype is not a valid NumPy dtype.
        """
    def push(self, data: np.ndarray) -> bool:
        """Attempts to add a NumPy array of data to the buffer.

        Args:
            data (np.ndarray): The array of data to push. Its dtype must match the buffer's declared dtype.

        Returns:
            bool: True if the data was successfully pushed, False if it would overflow the buffer.

        Raises:
            TypeError: If data_array has wrong type with respect to the buffer's declared dtype.
        """
    def pull(self, timeout: float = None) -> np.ndarray:
        """Retrieves a window of data as a NumPy array.
        Blocks until a window of window_size with at least slide_amount of
        new data is available or the provided timeout expires.

        Args:
            timeout (float, optional): The maximum time to wait for data. If None, waits indefinitely.

        Returns:
            np.ndarray: A NumPy array containing the data in the sliding window.
        """
    def flush(self) -> None:
        """Clears the buffer to its initial empty state and notifies any waiting threads."""
    def has_data(self) -> bool:
        """Checks if there is a full window of data ready to be pulled without blocking.

        Returns:
            bool: True if a call to pull() would not block waiting for data, False otherwise.
        """
