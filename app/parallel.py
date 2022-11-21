from asyncio import get_running_loop
from concurrent.futures import ProcessPoolExecutor
from typing import Callable, ParamSpec, TypeVar

POOL_SIZE = 4

T = TypeVar("T")
P = ParamSpec("P")


class Pool:
    _executor = None

    def __enter__(self, size=POOL_SIZE):
        assert Pool._executor is None
        Pool._executor = ProcessPoolExecutor(size)

    def __exit__(self, *_):
        assert Pool._executor is not None
        Pool._executor.shutdown()
        Pool._executor = None

    async def run(self, fn: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
        assert Pool._executor is not None
        return await get_running_loop().run_in_executor(Pool._executor, fn, *args, **kwargs)
