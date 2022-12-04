from typing import Generator

from app.path_finding.types import Location, Map, WeightedGraph

DIST_ADJC = 1.0
DIST_DIAG = 1.41421356237


class SquareGrid(WeightedGraph):

    def __init__(self, map: Map):
        self.map = map
        self.size = map.shape

    def neighbors(self, location: Location) -> Generator[Location, None, None]:
        (x, y) = location
        (sx, sy) = self.size

        for (dx, dy) in self._offsets():
            nx = x + dx
            ny = y + dy

            if 0 <= nx < sx and 0 <= ny < sy and self.map[ny, nx] == 0:
                yield (nx, ny)

    def cost(self, a: Location, b: Location) -> float:
        return DIST_DIAG if a[0] != b[0] and a[1] != b[1] else DIST_ADJC

    def _offsets(self) -> Generator[Location, None, None]:
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i != 0 or j != 0:
                    yield (i, j)
