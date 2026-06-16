import asyncio
from .adapter import AsyncBrickAdapter as AsyncBrickAdapter, AsyncProcessorAdapter as AsyncProcessorAdapter, AsyncSinkAdapter as AsyncSinkAdapter
from .constants import T_IN as T_IN, T_OUT as T_OUT
from _typeshed import Incomplete
from arduino.app_utils import Logger as Logger
from typing import Generic

logger: Incomplete

class PipelineTask:
    """Hierarchy root for classes that adapt bricks to the asyncio's tasks API."""
    adapter: Incomplete
    def __init__(self, adapter: AsyncBrickAdapter) -> None: ...
    def set_loop(self, loop: asyncio.AbstractEventLoop): ...
    async def start(self) -> asyncio.Task: ...
    async def stop(self) -> None:
        """Stops the task gracefully ."""

class SourceTask(PipelineTask, Generic[T_OUT]):
    adapter: AsyncBrickAdapter
    output_queue: Incomplete
    def __init__(self, adapter: AsyncBrickAdapter, queue_size: int = 1) -> None: ...

class ProcessorTask(PipelineTask, Generic[T_IN, T_OUT]):
    adapter: AsyncProcessorAdapter
    input_queue: asyncio.Queue[T_IN] | None
    output_queue: asyncio.Queue[T_OUT]
    def __init__(self, adapter: AsyncProcessorAdapter, queue_size: int = 1) -> None: ...

class SinkTask(PipelineTask, Generic[T_IN]):
    adapter: AsyncSinkAdapter
    input_queue: asyncio.Queue[T_IN] | None
    def __init__(self, adapter: AsyncSinkAdapter, queue_size: int = 1) -> None: ...
