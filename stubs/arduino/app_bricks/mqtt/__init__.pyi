import paho.mqtt.client as mqtt
from _typeshed import Incomplete
from arduino.app_utils import Logger as Logger, brick as brick
from typing import Callable

logger: Incomplete
DEFAULT_CLIENT_ID_PREFIX: str

class MQTT:
    """MQTT class for publishing and subscribing to MQTT topics."""
    broker_address: Incomplete
    broker_port: Incomplete
    client: Incomplete
    def __init__(self, broker_address: str, broker_port: int, username: str | None = None, password: str | None = None, topics: list[str] = None, client_id: str = None) -> None:
        """Initialize the MQTT Publisher.

        Args:
            broker_address (str): The address of the MQTT broker.
            broker_port (int): The port of the MQTT broker.
            username (str): The username for MQTT authentication. Defaults to None.
            password (str): The password for MQTT authentication. Defaults to None.
            topics (List[str], optional): List of topics to subscribe to upon connection. Defaults to None.
            client_id (str, optional): A unique client ID for the MQTT client. If None or empty, a random ID will be generated. Defaults to None.
        """
    def start(self) -> None:
        """Start the MQTT client and connect to the broker."""
    def stop(self) -> None:
        """Stop the MQTT client and disconnect from the broker."""
    def publish(self, topic: str, message: str | dict):
        """Publish a message to the MQTT topic.

        Args:
            topic (str): The topic to publish the message to.
            message (str|dict): The message to publish. Can be a string or a dictionary.

        Raises:
            ValueError: If the topic is an empty string.
            RuntimeError: If the publish operation fails.
        """
    def subscribe(self, topic: str):
        """Subscribe to a specified MQTT topic.

        Args:
            topic (str): The topic to subscribe to.

        Raises:
            ValueError: If the topic is an empty string.
            RuntimeError: If the subscription fails.
        """
    def on_message(self, topic: str, fn: Callable[[mqtt.Client, object, mqtt.MQTTMessage], None]):
        """Set the callback function for handling incoming messages on a specific topic.

        Args:
            topic (str): The topic to set the callback for.
            fn (Callable[[mqtt.Client, object, mqtt.MQTTMessage], None]): The callback function to handle incoming messages.

        Raises:
            ValueError: If the topic is an empty string or if fn is not callable.
            RuntimeError: If setting the callback fails.
        """
