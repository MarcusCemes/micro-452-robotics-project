from heapq import heappush, heappop
from typing import Generic, TypeVar

from app.path_finding.types import Location, Map

T = TypeVar("T")


class PriorityQueue(Generic[T]):

    def __init__(self):
        self.elements: list[tuple[float, T]] = []

    def empty(self) -> bool:
        return not self.elements

    def put(self, item: T, priority: float):
        heappush(self.elements, (priority, item))

    def get(self) -> T:
        return heappop(self.elements)[1]


def in_bounds(location: Location, size: tuple[int, int]) -> bool:
    (x, y), (w, h) = location, size
    return 0 <= x < w and 0 <= y < h
