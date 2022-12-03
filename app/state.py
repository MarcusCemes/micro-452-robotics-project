from dataclasses import dataclass, field
from typing import Any

from app.config import PHYSICAL_SIZE, SUBDIVISIONS
from app.utils.types import Signal, Vec2

ExtraObstacle = tuple[Vec2, Vec2]

OMITTED_KEYS = ["_dirty", "_changes"]


class ChangeListener:
    def __init__(self, state: "State"):
        self._state = state
        self._changes = dict()

    def get_patch(self) -> dict[str, Any]:
        changes = self._changes
        self._changes = dict()
        return changes

    def _add_change(self, key: str, value: Any):
        self._changes[key] = value

    async def wait_for_patch(self):
        await self._state.wait_changed()


@dataclass
class State:
    """
    The combined state of the application.

    The centralisation of all shared robot state allows it to be
    accessed from anywhere in the application and easily serialised
    and transmitted to clients that are connected via the web interface.
    """

    _dirty = Signal()
    _changes: list[ChangeListener] = field(default_factory=list)

    # == Filtering == #
    position: Vec2 | None = None
    orientation: float | None = None

    # == Navigation == #
    start: Vec2 | None = None
    end: Vec2 | None = None

    # == Global Navigation == #
    path: list[Vec2] | None = None
    next_waypoint_index: int | None = None
    obstacles: list[list[int]] = field(default_factory=list)
    extra_obstacles: list[ExtraObstacle] = field(default_factory=list)
    computation_time: float | None = None

    # == Vision == #
    subdivisions: int = SUBDIVISIONS
    physical_size: Vec2 = PHYSICAL_SIZE

    # == Local Navigation == #
    prox_sensors: list[float] | None = None
    relative_distances: list[float] = field(default_factory=list)
    reactive_control: bool | None = None

    # == Methods == #

    def __setattr__(self, name, value):
        try:
            for listener in self._changes:
                listener._add_change(name, value)

        except AttributeError:
            pass

        super().__setattr__(name, value)

    def json(self):
        return {
            key: value
            for (key, value) in self.__dict__.items()
            if key not in OMITTED_KEYS
        }

    def register_listener(self) -> ChangeListener:
        listener = ChangeListener(self)
        self._changes.append(listener)
        return listener

    def unregister_listener(self, listener: ChangeListener):
        self._changes.remove(listener)

    def changed(self):
        """Wake up all tasks waiting for the state to be changed."""
        self._dirty.trigger()

    async def wait_changed(self):
        """Wait for the state to be marked as changed."""
        await self._dirty.wait()


def create_patch(a: dict[str, Any], b: dict[str, Any]):
    return {
        key: value
        for key, value in b.items()
        if key not in a
        or type(value) is list and value is not a[key]
        or type(value) is not list and a[key] != value
    }


def normalise_obstacle(obstacle: ExtraObstacle) -> ExtraObstacle:
    """
    Rearrange obstacle vector components, such that the first vector points
    to the bottom-left of the obstacle (minimum components), vice-versa.
    """
    ((ax, ay), (bx, by)) = obstacle
    return ((min(ax, bx), min(ay, by)), (max(ax, bx), max(ay, by)))
