from asyncio import Event, wait_for
from asyncio.exceptions import TimeoutError
from collections import deque
from typing import Generic, TypeVar

Coords = tuple[int, int]
Vec2 = tuple[float, float]


class Signal:
    """
    A simplified wrapper around asyncio's `Event()` primitive.

    Tasks can wait for the signal to be triggered using `await signal.wait()`.
    The signal can then be triggered using `signal.trigger()` to wake up all waiting tasks.
    """

    def __init__(self):
        self._event = Event()

    def trigger(self):
        self._event.set()
        self._event.clear()

    async def wait(self, timeout: float | None = None):
        try:
            await wait_for(self._event.wait(), timeout)

        except TimeoutError:
            pass


T = TypeVar("T")


class Channel(Generic[T]):
    """
    An extension of Signal that supports sending and receiving messages
    asynchronously, similar to Go's channels.
    """

    def __init__(self):
        self._signal = Signal()
        self._messages = deque[T]()

    def send(self, value: T):
        self._messages.append(value)
        self._signal.trigger()

    async def recv(self, timeout: float | None = None) -> T | None:
        try:
            while len(self._messages) == 0:
                await wait_for(self._signal.wait(), timeout)

            return self._messages.popleft()

        except TimeoutError:
            pass
