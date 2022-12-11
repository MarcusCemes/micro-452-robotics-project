from dataclasses import dataclass, field
from typing import Any

import numpy as np
import numpy.typing as npt

from app.config import PHYSICAL_SIZE_CM, SUBDIVISIONS
from app.path_finding.types import Location, Map
from app.utils.types import Signal, Vec2

ObstacleQuad = tuple[Vec2, Vec2]


OMITTED_KEYS = ["_dirty", "_changes"]


class ChangeListener:
    def __init__(self, state: "State"):
        self._state = state
        self._changes = {}

    def get_patch(self) -> dict[str, Any]:
        patch = {key: make_serialisable(value) for key, value in self._changes.items()}

        self._changes = {}
        return patch

    def _add_change(self, key: str, value: Any):
        self._changes[key] = value

    async def wait_for_patch(self):
        if not self._changes:
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
    end: Vec2 | None = None
    arrived: bool | None = None

    # == Global Navigation == #
    path: list[Vec2] | None = None
    next_waypoint_index: int | None = None
    obstacles: npt.NDArray[np.int8] | None = None
    extra_obstacles: list[ObstacleQuad] = field(default_factory=list)
    boundary_map: Map | None = None
    computation_time: float | None = None
    nodes: list[Location] | None = None
    optimise: bool = False

    # == Vision == #
    subdivisions: int = SUBDIVISIONS
    physical_size: float = PHYSICAL_SIZE_CM
    last_detection: Vec2 | None = None
    last_detection_front: Vec2 | None = None
    last_orientation: float | None = None

    # == Local Navigation == #
    prox_sensors: list[float] | None = None
    relative_distances: list[float] = field(default_factory=list)
    reactive_control: bool | None = None
    dist: float | None = None

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
            key: make_serialisable(value)
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


def make_serialisable(value: Any):
    return value.tolist() if isinstance(value, np.ndarray) else value


def normalise_obstacle(obstacle: ObstacleQuad) -> ObstacleQuad:
    """
    Rearrange obstacle vector components, such that the first vector points
    to the bottom-left of the obstacle (minimum components), vice-versa.
    """

    ((ax, ay), (bx, by)) = obstacle
    return ((min(ax, bx), min(ay, by)), (max(ax, bx), max(ay, by)))
