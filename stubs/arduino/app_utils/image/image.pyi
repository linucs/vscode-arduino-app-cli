from PIL import Image, ImageDraw
from _typeshed import Incomplete
from arduino.app_utils import Logger as Logger

logger: Incomplete

class Shape:
    RECTANGLE: str
    CIRCLE: str

CONFIDENCE_MAP: Incomplete
FONT_PATH: str

def get_box_color(confid): ...
def get_image_type(image_bytes: bytes | Image.Image) -> str | None:
    """Detect the type of image from bytes or a PIL Image object.

    Returns:
        str: The image type in lowercase (e.g., 'jpeg', 'png').
        None if the image type cannot be determined.
    """
def get_image_bytes(image: str | Image.Image | bytes) -> bytes | None:
    """Convert different type of image objects to bytes."""
def draw_bounding_boxes(image: Image.Image | bytes, detection: dict, draw: ImageDraw.ImageDraw = None, shape: Shape = ...) -> Image.Image | None:
    """Draw bounding boxes on an image using PIL.

    The thickness of the box and font size are scaled based on image size.

    Args:
        image (Image.Image|bytes): The image to draw on, can be a PIL Image or bytes.
        detection (dict): A dictionary containing detection results with keys 'class_name', 'bounding_box_xyxy', and
            'confidence'.
        draw (ImageDraw.ImageDraw, optional): An existing ImageDraw object to use. If None, a new one is created.
        shape (Shape, optional): Shape of the bounding box. Defaults to rectangle.
        itself. Defaults to False.
    """
def draw_anomaly_markers(image: Image.Image | bytes, detection: dict, draw: ImageDraw.ImageDraw = None) -> Image.Image | None:
    """Draw bounding boxes on an image using PIL.

    The thickness of the box and font size are scaled based on image size.

    Args:
        image (Image.Image|bytes): The image to draw on, can be a PIL Image or bytes.
        detection (dict): A dictionary containing detection results with keys 'class_name', 'bounding_box_xyxy', and
            'score'.
        draw (ImageDraw.ImageDraw, optional): An existing ImageDraw object to use. If None, a new one is created.
    """
