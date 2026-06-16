from _typeshed import Incomplete
from arduino.app_internal.core.audio import AudioDetector as AudioDetector
from arduino.app_peripherals.microphone import BaseMicrophone as BaseMicrophone
from arduino.app_utils import Logger as Logger, brick as brick
from typing import Callable

logger: Incomplete

class KeywordSpotting(AudioDetector):
    """KeywordSpotting module for classifying audio data to detect keywords using a specified model.

    Processes continuous audio input to classify and detect specific keywords or phrases
    using pre-trained models. Supports both framework-provided models and custom models
    trained on Edge Impulse platform.
    """
    def __init__(self, mic: BaseMicrophone | None = None, confidence: float = 0.8, debounce_sec: float = 2.0) -> None:
        """Initialize the KeywordSpotting class.

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
                Must match the keyword as defined in the model.
            callback (Callable[[], None]): Callback function to run when the keyword is detected.
                Must take no parameters and return None.

        Raises:
            TypeError: If callback is not callable.
            ValueError: If callback accepts any argument.
        """
    def start(self) -> None:
        """Start the KeywordSpotting module and begin processing audio data.

        Begins continuous audio stream processing and keyword detection.
        """
    def stop(self) -> None:
        """Stop the KeywordSpotting module and release resources.

        Stops audio processing and releases microphone and model resources.
        """
