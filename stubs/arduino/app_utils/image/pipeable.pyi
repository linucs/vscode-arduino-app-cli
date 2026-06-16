from _typeshed import Incomplete
from typing import Callable

class PipeableFunction:
    """
    Wrapper class that adds pipe operator support to a function.

    This allows functions to be composed using the | operator in a left-to-right manner.
    """
    func: Incomplete
    args: Incomplete
    kwargs: Incomplete
    def __init__(self, func: Callable, *args, **kwargs) -> None:
        """
        Initialize a pipeable function.

        Args:
            func: The function to wrap
            *args: Positional arguments to partially apply
            **kwargs: Keyword arguments to partially apply
        """
    def __call__(self, *args, **kwargs):
        """Call the wrapped function with combined arguments."""
    def __ror__(self, other):
        """
        Right-hand side of pipe operator (|).

        This allows: value | pipeable_function

        Args:
            other: The value being piped into this function

        Returns:
            Result of applying this function to the value
        """
    def __or__(self, other):
        """
        Left-hand side of pipe operator (|).

        This allows: pipeable_function | other_function

        Args:
            other: Another function to compose with

        Returns:
            A new pipeable function that combines both
        """
