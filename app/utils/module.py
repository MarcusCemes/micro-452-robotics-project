from asyncio import Event, create_task
from traceback import print_exc
from typing import Any

from app.context import Context
from app.utils.console import *


class Module:
    """Abstract class for modules."""

    def __init__(self, ctx: Context):
        self.ctx = ctx

    def __enter__(self):
        self.ctx.node.add_variables_changed_listener(self._on_variables_changed)

        run = getattr(self, "run", None)
        self._task = create_task(run()) if callable(run) else None

    def __exit__(self, *_):
        self.ctx.node.remove_variables_changed_listener(self._on_variables_changed)

        if self._task is not None:
            self._task.cancel()

    def _on_variables_changed(self, _, variables):
        try:
            self.process_event(variables)

        except KeyError:
            pass

        except KeyboardInterrupt:
            pass

        except Exception:
            name = type(self).__name__
            warning(f"[Module/{name}] process_event() raised an exception")
            print_exc()

    async def _run(self):
        try:
            await self.run()

        except Exception:
            name = type(self).__name__
            error(f"[Module/{name}] run() raised an exception!")
            print_exc()

    async def run(self):
        """Method that runs in a background task."""

        await Event().wait()

    def process_event(self, _: dict[str, Any]):
        """Method that processes events from the Thymio driver."""

        pass
