from dataclasses import dataclass, field

from app.config import PHYSICAL_SIZE, SUBDIVISIONS
from app.utils.types import Coords, Signal, Vec2

Obstacle = tuple[Vec2, Vec2]


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
    next_waypoint_index: int | None = None
    obstacles: list[Coords] = field(default_factory=list)
    extra_obstacles: list[Obstacle] = field(default_factory=list)
    computation_time: float | None = None

    # == Vision == #
    subdivision: int = SUBDIVISIONS
    physical_size: Vec2 = PHYSICAL_SIZE

    # == Local Navigation == #
    prox_sensors: list[float] | None = None
    relative_distances: list[Coords] = field(default_factory=list)
    reactive_control: bool | None = None

    def changed(self):
        """Wake up all tasks waiting for the state to be changed."""
        self._dirty.trigger()

    async def wait_changed(self):
        """Wait for the state to be marked as changed."""
        await self._dirty.wait()


def normalise_obstacle(obstacle: Obstacle) -> Obstacle:
    """
    Rearrange obstacle vector components, such that the first vector points
    to the bottom-left of the obstacle (minimum components), vice-versa.
    """
    ((ax, ay), (bx, by)) = obstacle
    return ((min(ax, bx), min(ay, by)), (max(ax, bx), max(ay, by)))
