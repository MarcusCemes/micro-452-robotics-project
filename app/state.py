from asyncio import Event
from dataclasses import asdict, dataclass

Vec2 = tuple[float, float]

BOARD_SIZE_M = 2.0
NORTH = 1.57

@dataclass
class State:
    _stale = Event()

    position: Vec2
    orientation: float
    start: Vec2
    end: Vec2
    physical_size: Vec2
    path: list[Vec2] | None
    obstacles: list[tuple[Vec2, Vec2]]
    computation_time: float

    def json(self):
        return asdict(self)

    def mark_stale(self):
        self._stale.set()

    async def wait_for_stale(self):
        await self._stale.wait()
        self._stale.clear()


state = State(
    position=(0.5, 1.4),
    orientation=(NORTH),
    start=(0.4, 0.4),
    end=(1.6, 1.6),
    physical_size=(BOARD_SIZE_M, BOARD_SIZE_M),
    path=[],
    obstacles=[],
    computation_time=0.0
)
