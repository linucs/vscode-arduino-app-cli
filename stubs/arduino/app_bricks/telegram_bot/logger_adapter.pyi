import logging

class TelegramLoggerAdapter(logging.LoggerAdapter):
    '''Logger adapter that automatically adds Telegram context to log messages.

    This adapter prepends user ID, message ID, or chat ID to log messages,
    making it easier to trace logs when multiple users are interacting with
    the bot simultaneously.

    Args:
        logger: The base logger instance.
        user_id: Optional Telegram user ID.
        message_id: Optional Telegram message ID.
        chat_id: Optional Telegram chat ID.

    Examples:
        # With user and message context
        log = TelegramLoggerAdapter(logger, user_id=12345, message_id=67890)
        log.info("Processing request")
        # Output: "[user=12345, msg=67890] Processing request"

        # With only chat context
        log = TelegramLoggerAdapter(logger, chat_id=12345)
        log.info("Message sent")
        # Output: "[chat=12345] Message sent"
    '''
    def __init__(self, logger: logging.Logger, user_id: int | None = None, message_id: int | None = None, chat_id: int | None = None) -> None: ...
    def process(self, msg, kwargs):
        """Prepend context information to log message.

        Args:
            msg: The log message.
            kwargs: Additional keyword arguments.

        Returns:
            Tuple of (modified_message, kwargs).
        """
