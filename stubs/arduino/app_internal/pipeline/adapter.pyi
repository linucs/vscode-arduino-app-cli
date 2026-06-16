import asyncio
from .limiter import AsyncRateLimiter as AsyncRateLimiter
from _typeshed import Incomplete
from arduino.app_utils import Logger as Logger
from typing import Any

logger: Incomplete

class AsyncBrickAdapter:
    """Base class for brick adapters, normalizing to an async API."""
    original_brick: Incomplete
    rate_limit: Incomplete
    def __init__(self, original_brick: Any, rate_limit: int | None = None) -> None: ...
    def set_loop(self, loop: asyncio.AbstractEventLoop): ...
    async def start(self):
        """Normalized async start method."""
    async def stop(self):
        """Normalized async stop method."""

class AsyncSourceAdapter(AsyncBrickAdapter):
    """Adapter for async sources."""
    def __init__(self, original_brick: Any, rate_limit: int | None = None) -> None: ...
    async def produce(self, *args: Any) -> Any:
        """Normalized async produce, calls original async method."""

class AsyncBlockingSourceAdapter(AsyncBrickAdapter):
    """Adapter for synchronous sources that might block indefinitely.
    Manages a daemon thread internally to avoid blocking the event loop.
    """
    def __init__(self, original_brick: Any, rate_limit: int | None = None) -> None: ...
    async def start(self) -> None:
        """Start the original brick and the internal blocking producer thread."""
    async def stop(self) -> None:
        """Signal the producer thread and the original brick to stop."""
    def unblock_producer(self) -> None:
        """Signals the producer thread and injects sentinel to unblock consumer."""
    async def produce(self, *args: Any) -> Any:
        """Normalized async produce, gets data from internal queue populated by the daemon thread
        and applies emission rate limit.
        """

class AsyncProcessorAdapter(AsyncBrickAdapter):
    def __init__(self, original_brick: Any, rate_limit: int | None = None) -> None: ...
    async def process(self, *args: Any) -> Any: ...

class AsyncSinkAdapter(AsyncBrickAdapter):
    def __init__(self, original_brick: Any, rate_limit: int | None = None) -> None: ...
    async def consume(self, *args: Any) -> Any: ...

def create_adapter(brick: Any, brick_type: str, rate_limit: int | None = None) -> AsyncBrickAdapter:
    """Factory function that creates the appropriate adapter for the provided brick_type."""
