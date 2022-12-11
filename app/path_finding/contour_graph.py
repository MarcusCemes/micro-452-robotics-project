from typing import Generator

import numpy as np
from numpy.typing import NDArray
from scipy.signal import convolve2d

from app.path_finding.path_optimiser import PathOptimiser, norm
from app.path_finding.types import Location, Map, WeightedGraph


class ContourGraph(WeightedGraph):
    """
    This is an alternate graph implementation that uses obstacle contours.
    It is not utilised in the final product, but can be swapped in for GridGraph as
    it implements the WeightedGraph interface.
    """

    def __init__(self, map: Map):
        self.map = map
        self.size = map.shape
        self.path_opt = PathOptimiser(map)

        boundary = self._compile_map(map)
        self.nodes = self._extract_nodes(boundary)

    def neighbors(
        self, location: Location, end: Location
    ) -> Generator[Location, None, None]:
        if self.path_opt.free_path(location, end):
            yield end

        for node in self.nodes:
            if node == location or node == end:
                continue

            if self.path_opt.free_path(location, node):
                yield node

    def cost(self, a: Location, b: Location) -> float:
        return norm(b, a)

    def _compile_map(self, map: Map) -> Map:
        boundary = convolve2d(
            map, self._kernel(), mode="same", boundary="fill", fillvalue=0
        )

        return np.logical_and(map == 0, boundary > 0)

    def _extract_nodes(self, boundary: Map) -> list[Location]:
        return [(x, y) for (y, x), value in np.ndenumerate(boundary) if value == 1]

    def _kernel(self) -> NDArray:
        return np.ones((3, 3), dtype=np.uint8)
