from _typeshed import Incomplete
from arduino.app_internal.core import EdgeImpulseRunnerFacade as EdgeImpulseRunnerFacade
from arduino.app_peripherals.microphone import BaseMicrophone as BaseMicrophone, Microphone as Microphone
from arduino.app_utils import Logger as Logger, SlidingWindowBuffer as SlidingWindowBuffer, brick as brick
from typing import Callable

logger: Incomplete

class AudioDetector(EdgeImpulseRunnerFacade):
    """AudioDetector module for detecting sounds and classifying audio using a specified model."""
    confidence: Incomplete
    model_info: Incomplete
    handlers: Incomplete
    handlers_lock: Incomplete
    def __init__(self, mic: BaseMicrophone | None = None, confidence: float = 0.8, debounce_sec: float = 2.0) -> None:
        """Initialize the AudioDetector class.

        Args:
            mic (BaseMicrophone): Microphone instance for audio input.
                If None, a default Microphone will be initialized.
            confidence (float): Confidence level for detection between 0.0 and 1.0.
                Default is 0.8 (80%). Higher values reduce false positives.
            debounce_sec (float): Minimum seconds between repeated detections
                of the same keyword. Default is 2.0 seconds.

        Raises:
            ValueError: If the model information cannot be retrieved or if the model parameters are incomplete.
        """
    def on_detect(self, keyword: str, callback: Callable[[], None]):
        """Register a callback function to be invoked when a specific keyword is detected.

        Args:
            keyword (str): The keyword to check for in the classification results.
            callback (callable): a callback function to handle the keyword spotted.

        Raises:
            TypeError: If callback is not callable.
            ValueError: If callback accepts any argument.
        """
    def start(self) -> None: ...
    def stop(self) -> None: ...
    @staticmethod
    def get_best_match(item: dict, confidence: float) -> tuple[str, float] | None:
        """Extract the best matched keyword from the classification results.

        Args:
        item (dict): The classification result from the inference.
        confidence (float): The confidence threshold for classification.

        Returns:
        tuple[str, float] | None: The best matched keyword and its confidence, or None if no match is found.

        Raises:
        ValueError: If confidence level is not provided.
        """
