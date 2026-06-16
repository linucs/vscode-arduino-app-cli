class AsyncRateLimiter:
    """Helper class for async rate limiting."""
    def __init__(self, calls_per_second: int) -> None: ...
    async def wait(self) -> None:
        """Wait if necessary to maintain the desired rate."""
