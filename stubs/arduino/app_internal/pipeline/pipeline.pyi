from .adapter import create_adapter as create_adapter
from .task import PipelineTask as PipelineTask, ProcessorTask as ProcessorTask, SinkTask as SinkTask, SourceTask as SourceTask
from _typeshed import Incomplete
from arduino.app_utils import Logger as Logger
from typing import Any

logger: Incomplete

class Pipeline:
    def __init__(self, debug: bool = False) -> None: ...
    def add_source(self, brick: Any, rate_limit: int | None = None, queue_size: int = 1): ...
    def add_processor(self, brick: Any, rate_limit: int | None = None, queue_size: int = 1): ...
    def add_sink(self, brick: Any, rate_limit: int | None = None, queue_size: int = 1): ...
    def start(self) -> None:
        """Starts the pipeline in a background thread."""
    def stop(self) -> None:
        """Stops the pipeline gracefully."""
