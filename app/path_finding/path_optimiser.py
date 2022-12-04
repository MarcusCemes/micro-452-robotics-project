from math import sqrt
from typing import Generator

from app.path_finding.types import Location, Map
from app.path_finding.utils import in_bounds


class PathOptimiser:

    def __init__(self, map: Map):
        self.map = map
        self.size = map.shape

    def optimise(self, path: list[Location]) -> list[Location]:
        if len(path) <= 2:
            return path

        i = 1
        optimised_path = path

        while i != len(path) - 1:
            if self.free_path(optimised_path[i - 1], optimised_path[i + 1]):
                optimised_path.pop(i)
                i = 1
            else:
                i += 1

        return optimised_path

    def free_path(self, a: Location, b: Location) -> bool:
        for (x, y) in self.intermediate_nodes(a, b):
            if self.map[y, x] != 0:
                return False

        return True

    def intermediate_nodes(self, a: Location, b: Location) -> Generator[Location, None, None]:

        for loc in raytrace(a, b):
            if in_bounds(loc, self.size):
                yield loc

    def adjacent_nodes(self, a: Location, b: Location) -> bool:
        (x1, y1), (x2, y2) = a, b
        return abs(x1 - x2) <= 1 and abs(y1 - y2) <= 1


def raytrace(a: Location, b: Location) -> Generator[Location, None, None]:
    """
    An integer-only implementation of a supercover line algorithm.
    Enumerates all grid cells that intersect with a line segment.
    See https://playtechs.blogspot.com/2007/03/raytracing-on-grid.html
    """
    (x1, y1), (x2, y2) = a, b

    dx = abs(x2 - x1)
    dy = abs(y2 - y1)

    x = x1
    y = y1

    x_inc = 1 if x2 > x1 else -1
    y_inc = 1 if y2 > y1 else -1

    error = dx - dy
    dx *= 2
    dy *= 2

    n = 1 + dx + dy

    for _ in range(n, 0, -1):
        yield x, y

        if error > 0:
            x += x_inc
            error -= dy

        else:
            y += y_inc
            error += dx


def norm(a: Location, b: Location) -> float:
    """Fast Euclidean distance between two points."""
    (x1, y1) = a
    (x2, y2) = b

    x = float(x1 - x2)
    y = float(y1 - y2)

    return sqrt(x * x + y * y)
