from typing import Generator, Protocol

from numpy import int8
from numpy.typing import NDArray

Location = tuple[int, int]
Map = NDArray[int8]


class WeightedGraph(Protocol):

    map: Map
    nodes: list[Location]

    def neighbors(
        self,
        location: Location,
        end: Location,
    ) -> Generator[Location, None, None]:
        raise NotImplementedError

    def cost(self, origin: Location, target: Location) -> float:
        raise NotImplementedError


class Algorithm(Protocol):

    def find_path(
        self,
        start: Location,
        end: Location,
    ) -> list[Location]:
        raise NotImplementedError
