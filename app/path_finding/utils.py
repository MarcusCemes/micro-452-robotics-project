from heapq import heappush, heappop
from typing import Generic, TypeVar

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


def clamp(value: int, a: int, b: int) -> int:
    return max(a, min(value, b))
