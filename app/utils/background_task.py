from asyncio import create_task
from traceback import print_exception

from app.utils.console import *


class BackgroundTask:

    def __enter__(self):
        self._task = create_task(self._run())
        return self

    def __exit__(self, *_):
        self._task.cancel()

    async def _run(self):
        try:
            await self.run()

        except Exception as e:
            name = type(self).__name__
            error(f"[{name}/BackgroundTask] Coroutine raised an exception!")
            print_exception(e)

    async def run(self):
        name = type(self).__name__
        warning(f"[{name}/BackgroundTask] run() not implemented!")
