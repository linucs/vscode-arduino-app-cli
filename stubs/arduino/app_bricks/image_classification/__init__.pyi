from _typeshed import Incomplete
from arduino.app_internal.core import EdgeImpulseRunnerFacade as EdgeImpulseRunnerFacade
from arduino.app_utils import Logger as Logger, brick as brick

logger: Incomplete

class ImageClassification(EdgeImpulseRunnerFacade):
    """Module for image analysis and content classification using machine learning.

    This module processes an input image and returns:
    - Corresponding class labels
    - Confidence scores for each classification

    """
    confidence: Incomplete
    def __init__(self, confidence: float = 0.3) -> None:
        """Initialize the ImageClassification module.

        Args:
            confidence (float, optional): Minimum confidence threshold for
                classification results. Defaults to 0.3.
        """
    def classify_from_file(self, image_path: str, confidence: float = None) -> dict | None:
        """Process a local image file to be classified.

        Args:
            image_path (str): Path to the image file on the local file system.
            confidence (float): Minimum confidence threshold for classification results. Default is None (use module defaults).

        Returns:
            dict: Classification results containing class names and confidence, or None if an error occurs.
        """
    def classify(self, image_bytes, image_type: str = 'jpg', confidence: float = None) -> dict | None:
        """Process an in-memory image to be classified.

        Args:
            image_bytes: Can be raw bytes (e.g., from a file or stream) or a preloaded PIL image.
            image_type (str): The image format ('jpg', 'jpeg', or 'png'). Required if using raw bytes. Defaults to 'jpg'.
            confidence (float): Minimum confidence threshold for classification results. Default is None (use module defaults).

        Returns:
            dict: Classification results containing class names and confidence, or None if an error occurs.
        """
    def process(self, item):
        """Process an item to classify objects in an image.

        This method supports two input formats:
        - A string path to a local image file.
        - A dictionary containing raw image bytes under the 'image' key, and optionally an 'image_type' key (e.g., 'jpg', 'png').

        Args:
            item: A file path (str) or a dictionary with the 'image' and 'image_type' keys (dict).
                'image_type' is optional while 'image' contains image as bytes.

        Returns:
            dict: Classification results or None if an error occurs.
        """
