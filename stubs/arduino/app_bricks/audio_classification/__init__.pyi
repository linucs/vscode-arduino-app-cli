from _typeshed import Incomplete
from arduino.app_internal.core.audio import AudioDetector as AudioDetector
from arduino.app_peripherals.microphone import Microphone as Microphone
from arduino.app_utils import Logger as Logger, brick as brick
from typing import Callable

logger: Incomplete

class AudioClassificationException(Exception):
    """Custom exception for AudioClassification errors."""

class AudioClassification(AudioDetector):
    """AudioClassification module for detecting sounds and classifying audio using a specified model."""
    def __init__(self, mic: Microphone = None, confidence: float = 0.8) -> None:
        """Initialize the AudioClassification class.

        Args:
            mic (Microphone, optional): Microphone instance used as the audio source. If None, a default Microphone will be initialized.
            confidence (float, optional): Minimum confidence threshold (0.0–1.0) required
                for a detection to be considered valid. Defaults to 0.8 (80%).

        Raises:
            ValueError: If the model information cannot be retrieved, or if model parameters are missing or incomplete.
        """
    def on_detect(self, class_name: str, callback: Callable[[], None]):
        """Register a callback function to be invoked when a specific class is detected.

        Args:
            class_name (str): The class to check for in the classification results.
                Must match one of the classes defined in the loaded model.
            callback (callable): Function to execute when the class is detected.
                The callback must take no arguments and return None.

        Raises:
            TypeError: If `callback` is not callable.
            ValueError: If `callback` accepts any argument.
        """
    def start(self) -> None:
        """Start real-time audio classification.

        Begins capturing audio from the configured microphone and
        continuously classifies the incoming audio stream until stopped.
        """
    def stop(self) -> None:
        """Stop real-time audio classification.

        Terminates audio capture and releases any associated resources.
        """
    @staticmethod
    def classify_from_file(audio_path: str, confidence: float = 0.8) -> dict | None:
        """Classify audio content from a WAV file.

        Supported sample widths:
            - 8-bit unsigned
            - 16-bit signed
            - 24-bit signed
            - 32-bit signed

        Args:
            audio_path (str): Path to the `.wav` audio file to classify.
            confidence (float, optional): Minimum confidence threshold (0.0–1.0) required
                for a detection to be considered valid. Defaults to 0.8 (80%).

        Returns:
            dict | None: A dictionary with keys:
            - ``class_name`` (str): The detected sound class.
            - ``confidence`` (float): Confidence score of the detection.
            Returns None if no valid classification is found.

        Raises:
            AudioClassificationException: If the file cannot be found, read, or processed.
            ValueError: If the file uses an unsupported sample width.
        """
