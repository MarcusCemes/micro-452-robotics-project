from asyncio import get_running_loop
from concurrent.futures import ProcessPoolExecutor
from typing import Callable, ParamSpec, TypeVar

from app.config import POOL_SIZE

T = TypeVar("T")
P = ParamSpec("P")


class Pool:
    """Simple process pool for offloading expensive CPU computation."""

    def __init__(self):
        self.executor = None

    def __enter__(self, size=POOL_SIZE):
        assert self.executor is None
        self.executor = ProcessPoolExecutor(size)
        return self

    def __exit__(self, *_):
        assert self.executor is not None
        self.executor.shutdown()
        self.executor = None

    async def run(self, fn: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
        """Run a function in the pool and return the result."""

        assert self.executor is not None
        loop = get_running_loop()
        return await loop.run_in_executor(self.executor, fn, *args, **kwargs)
