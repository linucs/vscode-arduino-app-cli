from .detection import Detection as Detection
from PIL.Image import Image as Image
from _typeshed import Incomplete

font_size: int
font: Incomplete

def draw_bounding_boxes(frame: Image, detections: list[Detection]) -> Image: ...
def draw_bounding_box(frame: Image, detection: Detection) -> Image:
    """Draws a bounding box and label on an image for a detected QR code or barcode.

    This function overlays a green polygon around the detected code area and
    adds a text label above (or below) the bounding box with the code type and content.

    Args:
        frame (Image): The PIL Image object to draw on. This image will be modified in-place.
        detection (Detection): The detection result containing the code's content, type, and corner coordinates.

    Returns:
        Image: The annotated image with a bounding box and label drawn.
    """
