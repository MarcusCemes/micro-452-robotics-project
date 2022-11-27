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
        return self

    def __exit__(self, *_):
        self.ctx.node.remove_variables_changed_listener(
            self._on_variables_changed)

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
