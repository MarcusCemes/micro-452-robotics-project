from asyncio import create_task
from traceback import print_exc

from app.utils.console import *


class BackgroundTask:

    def __enter__(self):
        self._task = create_task(self._run())

    def __exit__(self, *_):
        self._task.cancel()

    async def _run(self):
        try:
            await self.run()

        except Exception:
            name = type(self).__name__
            error(f"[{name}/BackgroundTask] Coroutine raised an exception!")
            print_exc()

    async def run(self):
        name = type(self).__name__
        warning(f"[{name}/BackgroundTask] run() not implemented!")
