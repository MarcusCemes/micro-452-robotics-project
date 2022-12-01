from asyncio import create_task
from traceback import format_exc
from typing import Any

from app.context import Context
from app.utils.console import *


class ThymioEventProcessor:
    def __init__(self, ctx: Context):
        self.ctx = ctx

    def __enter__(self):
        self.ctx.node.add_variables_changed_listener(
            self._on_variables_changed)

        run = getattr(self, "run", None)
        self._task = create_task(run()) if callable(run) else None

        return self

    def __exit__(self, *_):
        self.ctx.node.remove_variables_changed_listener(
            self._on_variables_changed)

        if self._task:
            self._task.cancel()

    def _on_variables_changed(self, _, variables):
        try:
            self.process_event(variables)

        except KeyError:
            pass

        except KeyboardInterrupt:
            pass

        except Exception:
            warning("[ThymioEventProcessor] process_event() raised an exception")
            print(format_exc())

    def process_event(self, _: dict[str, Any]):
        warning("[ThymioEventProcessor] process_event() not implemented!")
