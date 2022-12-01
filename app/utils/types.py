from asyncio import Event, wait_for


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
        await wait_for(self._event.wait(), timeout)
