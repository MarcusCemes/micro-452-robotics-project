from asyncio import create_task

from app.utils.console import *


class BackgroundTask:

    def __enter__(self):
        self._task = create_task(self.run())
        return self

    def __exit__(self, *_):
        self._task.cancel()

    async def run(self):
        warning("[BackgroundTask] run() not implemented!")
