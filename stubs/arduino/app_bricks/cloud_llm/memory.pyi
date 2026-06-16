from .utils import logger as logger
from langchain_core.messages import BaseMessage as BaseMessage

class WindowedChatMessageHistory:
    """A chat history store that automatically keeps a window of the last k messages."""
    k: int
    def __init__(self, k: int, system_message: str = '') -> None: ...
    def add_messages(self, messages: list[BaseMessage]) -> None: ...
    def get_messages(self) -> list[BaseMessage]:
        """Get all messages in the history, including system message if set."""
    def clear(self) -> None:
        """Clear the message history."""
