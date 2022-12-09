from typing import Callable, ParamSpec, TypeVar

T = TypeVar("T")
P = ParamSpec("P")


class MockPool:

    async def run(self, fn: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
        return fn(*args, **kwargs)
