from typing import Generator

from app.path_finding.types import Location, Map, WeightedGraph
from app.path_finding.utils import in_bounds

DIST_ADJC = 1.0
DIST_DIAG = 1.41421356237


class GridGraph(WeightedGraph):
    """
    Standard grid graph implementation for Dijkstra. Splits the
    map into a grid of nodes, and connects them if they are directly adjacent
    (vertically, horizontally, or diagonally). The between directly adjacent
    nodes is 1.0, and the between diagonally adjacent nodes is sqrt(2).
    """

    def __init__(self, map: Map):
        self.map = map
        self.size = map.shape
        self.nodes = []

    def neighbors(self, location: Location, _) -> Generator[Location, None, None]:
        (x, y) = location

        for (dx, dy) in self._offsets():
            nx = x + dx
            ny = y + dy

            if in_bounds((nx, ny), self.size) and self.map[ny, nx] == 0:
                yield (nx, ny)

    def cost(self, a: Location, b: Location) -> float:
        return DIST_DIAG if a[0] != b[0] and a[1] != b[1] else DIST_ADJC

    def _offsets(self) -> Generator[Location, None, None]:
        """Iterates over all index offsets adjacent to a node."""

        for i in range(-1, 2):
            for j in range(-1, 2):
                if i != 0 or j != 0:
                    yield (i, j)
