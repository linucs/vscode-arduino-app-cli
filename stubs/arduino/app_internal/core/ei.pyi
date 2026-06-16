from _typeshed import Incomplete
from arduino.app_internal.core import load_brick_compose_file as load_brick_compose_file, resolve_address as resolve_address
from arduino.app_utils import HttpClient as HttpClient, Logger as Logger
from arduino.app_utils.image import get_image_bytes as get_image_bytes, get_image_type as get_image_type

logger: Incomplete

class EdgeImpulseModelInfo:
    """Class to hold Edge Impulse model information."""
    name: Incomplete
    project_id: Incomplete
    model_type: Incomplete
    axis_count: Incomplete
    frequency: Incomplete
    image_input_height: Incomplete
    image_input_width: Incomplete
    input_features_count: Incomplete
    label_count: Incomplete
    labels: Incomplete
    interval_ms: Incomplete
    thresholds: Incomplete
    def __init__(self, model_info: dict) -> None:
        """Initialize the EdgeImpulseModelInfo with model information."""

class EdgeImpulseRunnerFacade:
    """Facade for Edge Impulse Object Detection and Classification."""
    url: Incomplete
    def __init__(self) -> None:
        """Initialize the EdgeImpulseRunnerFacade with the API path.

        Raises:
            RuntimeError: If the Edge Impulse runner address cannot be resolved.
        """
    def infer_from_file(self, image_path: str) -> dict | None: ...
    def infer_from_image(self, image_bytes, image_type: str = 'jpg') -> dict | None: ...
    def process(self, item):
        """Process an item to detect objects in an image.

        Args:
            item: A file path (str) or a dictionary with the 'image' and 'image_type' keys (dict).
                'image_type' is optional while 'image' contains image as bytes.
        """
    @classmethod
    def infer_from_features(cls, features: list) -> dict | None:
        """
        Infer from features using the Edge Impulse API.

        Args:
            cls: The class method caller.
            features (list): A list of features to send to the Edge Impulse API.

        Returns:
            dict | None: The response from the Edge Impulse API as a dictionary, or None if an error occurs.
        """
    @classmethod
    def get_model_info(cls, url: str = None) -> EdgeImpulseModelInfo | None:
        """Get model information from the Edge Impulse API.

        Args:
            cls: The class method caller.
            url (str): The base URL of the Edge Impulse API. If None, it will be determined automatically.

        Returns:
            model_info (EdgeImpulseModelInfo | None): An instance of EdgeImpulseModelInfo containing model details, None if an error occurs.
        """
    @staticmethod
    def parse_model_info_message(model_info: dict) -> EdgeImpulseModelInfo | None:
        """Parse Edge Impulse model definition message.

        Args:
            model_info (dict): A dictionary containing model information.

        Returns:
            EdgeImpulseModelInfo | None: An instance of EdgeImpulseModelInfo if parsing is successful, None otherwise.
        """
