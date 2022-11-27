from dataclasses import dataclass, field

from app.config import PHYSICAL_SIZE, SUBDIVISIONS
from app.types import Coords, Signal, Vec2


@dataclass
class State:
    """
    The combined state of the application.

    The centralisation of all shared robot state allows it to be
    accessed from anywhere in the application and easily serialised
    and transmitted to clients that are connected via the web interface.
    """

    _dirty = Signal()

    # == Filtering == #
    position: Vec2 | None = None
    orientation: float | None = None

    # == Navigation == #
    start: Vec2 | None = None
    end: Vec2 | None = None

    # == Global Navigation == #
    path: list[Vec2] | None = None
    obstacles: list[Coords] = field(default_factory=list)
    computation_time: float | None = None

    # == Vision == #
    subdivision: int = SUBDIVISIONS
    physical_size: Vec2 = PHYSICAL_SIZE

    def changed(self):
        """Wake up all tasks waiting for the state to be changed."""
        self._dirty.trigger()

    async def wait_changed(self):
        """Wait for the state to be marked as changed."""
        await self._dirty.wait()
