from PIL import Image as Image
from _typeshed import Incomplete
from arduino.app_internal.core import EdgeImpulseRunnerFacade as EdgeImpulseRunnerFacade
from arduino.app_utils import Logger as Logger, brick as brick
from arduino.app_utils.image import Shape as Shape, draw_bounding_boxes as draw_bounding_boxes
from typing import Any

logger: Incomplete

class ObjectDetection(EdgeImpulseRunnerFacade):
    """Module for object detection in images using a specified machine learning model.

    This module processes an input image and returns:
    - Bounding boxes for detected objects
    - Corresponding class labels
    - Confidence scores for each detection
    """
    confidence: Incomplete
    def __init__(self, confidence: float = 0.3) -> None:
        """Initialize the ObjectDetection module.

        Args:
            confidence (float): Minimum confidence threshold for detections. Default is 0.3 (30%).

        Raises:
            ValueError: If model information cannot be retrieved.
        """
    def detect_from_file(self, image_path: str, confidence: float = None) -> dict | None:
        """Process a local image file to detect and identify objects.

        Args:
            image_path: Path to the image file on the local file system.
            confidence: Minimum confidence threshold for detections. Default is None (use module defaults).

        Returns:
            dict: Detection results containing class names, confidence, and bounding boxes.
        """
    def detect(self, image_bytes, image_type: str = 'jpg', confidence: float = None) -> dict[str, list[Any]] | None:
        """Process an in-memory image to detect and identify objects.

        Args:
            image_bytes: Can be raw bytes (e.g., from a file or stream) or a preloaded PIL image.
            image_type: The image format ('jpg', 'jpeg', or 'png'). Required if using raw bytes. Defaults to 'jpg'.
            confidence: Minimum confidence threshold for detections. Default is None (use module defaults).

        Returns:
            dict: Detection results containing class names, confidence, and bounding boxes.
        """
    def draw_bounding_boxes(self, image: Image.Image | bytes, detections: dict) -> Image.Image | None:
        """Draw bounding boxes on an image enclosing detected objects using PIL.

        Args:
            image: The input image to annotate. Can be a PIL Image object or raw image bytes.
            detections: Detection results containing object labels and bounding boxes.

        Returns:
            Image with bounding boxes and key points drawn.
            None if input image or detections are invalid.
        """
    def process(self, item):
        """Process an item to detect objects in an image.

        This method supports two input formats:
        - A string path to a local image file.
        - A dictionary containing raw image bytes under the 'image' key, and optionally an 'image_type' key (e.g., 'jpg', 'png').

        Args:
            item: A file path (str) or a dictionary with the 'image' and 'image_type' keys (dict).
                'image_type' is optional while 'image' contains image as bytes.
        """
