import logging
from _typeshed import Incomplete

class Logger(logging.Logger):
    """A simple logger class that extends Python's logging.Logger.
    Log levels can also be customized using the APP_BRICKS_LOG_LEVEL environment variable (FATAL, CRITICAL, ERROR, WARNING, INFO, DEBUG).

    Args:
        name (str): The name of the logger. You can use the dot syntax (parent.child) to create a hierarchy of loggers.
        level (int or str): The logging level. Defaults to logging.WARNING.

    Examples:
        logger = Logger('my_logger')
        logger.error('This is an error message and will be printed')
        logger.warning('This is a warning message and will be printed')
        logger.info('This is an info message and won't be printed by default')
        logger.debug('This is a debug message and won't be printed by default')
        logger.print('This will always be printed, regardless of the level')
    """
    handlers: Incomplete
    def __init__(self, name: str, level: int = ...) -> None: ...
    def process(self, msg): ...
    def consume(self, msg) -> None: ...
