from _typeshed import Incomplete
from arduino.app_internal.core import EdgeImpulseRunnerFacade as EdgeImpulseRunnerFacade
from arduino.app_utils import Logger as Logger, brick as brick

logger: Incomplete

class VisualAnomalyDetection(EdgeImpulseRunnerFacade):
    """Module for detecting **visual anomalies** in images using a specified model.

    This module processes an input image and returns:
    - Global anomaly metrics (`anomaly_max_score`, `anomaly_mean_score`), when available.
    - A list of localized anomaly detections with label, score, and bounding boxes.

    Notes:
        - Bounding boxes are returned as `[x_min, y_min, x_max, y_max]` (float).
        - Methods return `None` when input is invalid or when the model output
          does not contain expected anomaly fields.
    """
    def __init__(self) -> None: ...
    def detect_from_file(self, image_path: str) -> dict:
        '''Process a local image file to detect anomalies.

        Args:
            image_path (str): Path to the image file on the local file system.

        Returns:
            dict | None: A dictionary with anomaly information, or `None` on error.
                Example successful payload:
                {
                    "anomaly_max_score": <float>,              # optional, if provided by model
                    "anomaly_mean_score": <float>,             # optional, if provided by model
                    "detection": [
                        {
                            "class_name": <str>,
                            "score": <float>,                   # anomaly score for this region
                            "bounding_box_xyxy": [x1, y1, x2, y2]
                        },
                        ...
                    ]
                }

            - Returns `None` if `image_path` is falsy or if the inference result
              does not include anomaly data.
        '''
    def detect(self, image_bytes, image_type: str = 'jpg') -> dict:
        """Process an in-memory image to detect anomalies.

        Args:
            image_bytes: Raw image bytes (e.g., from a file or camera) or a PIL Image.
            image_type (str): Image format ('jpg', 'jpeg', 'png'). Required when passing raw bytes.
                              Defaults to 'jpg'.

        Returns:
            dict | None: A dictionary with anomaly information, or `None` on error.
                See `detect_from_file` for the response schema.

            - Returns `None` if `image_bytes` or `image_type` is missing/invalid.
        """
    def process(self, item):
        '''Process an item to detect anomalies (file path or in-memory image).

        This method supports two input formats:
        - A string path to a local image file.
        - A dictionary containing raw image bytes under the `\'image\'` key, and
          optionally an `\'image_type\'` key (e.g., `\'jpg\'`, `\'png\'`).

        Args:
            item (str | dict): File path or a dict with `\'image\'` (bytes/PIL) and
                optional `\'image_type\'` (str).

        Returns:
            dict | None: Normalized anomaly payload or `None` if an error occurs or
            the result lacks anomaly data.

        Example:
            process("path/to/image.jpg")
            # or
            process({"image": image_bytes, "image_type": "png"})
        '''
