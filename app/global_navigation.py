from time import perf_counter
from typing import Type

import numpy as np
from numpy import int8
from numpy.typing import NDArray
from scipy.signal import convolve2d

from app.config import SAFE_DISTANCE
from app.context import Context
from app.path_finding.dijkstra import Dijkstra
from app.path_finding.grid_graph import GridGraph
from app.path_finding.types import Algorithm, Location, Map
from app.state import ObstacleQuad
from app.utils.background_task import BackgroundTask
from app.utils.console import *
from app.utils.math import clamp
from app.utils.types import Vec2


class GlobalNavigation(BackgroundTask):

    def __init__(self, ctx: Context, algorithm: Type[Algorithm] = Dijkstra):
        super().__init__()
        self.ctx = ctx
        self.algorithm = algorithm
        self.computedOnce = False

    async def run(self):
        while True:
            await self.ctx.scene_update.wait()
            await self._recompute_path()

    async def _recompute_path(self):
        start = self.ctx.state.position
        end = self.ctx.state.end

        if not start or not end:
            return False

        # TODO Check if obstacle array is defined/ready?

        map = self._generate_map()
        self.ctx.state.boundary_map = map
        self.ctx.state.changed()

        graph = GridGraph(map)

        self.ctx.state.nodes = graph.nodes
        self.ctx.state.changed()

        if(self.computedOnce == False):
            self.computedOnce = True
            algo = Dijkstra(graph, self.ctx.state.optimise)
            start = self._to_location(start)
            end = self._to_location(end)

            path, time = await self.ctx.pool.run(profile_algo, start, end, algo)

            if path is not None:
                path = self._path_to_coords(path)
            
            self.ctx.state.path = path
            self.ctx.state.computation_time = time
            self.ctx.state.next_waypoint_index = 0
            self.ctx.state.changed()

        return True

    def _generate_map(self) -> Map:
        map = np.array(self.ctx.state.obstacles, dtype=np.int8)

        for obstacle in self.ctx.state.extra_obstacles:
            (x1, y1), (x2, y2) = self._obstacle_to_location(obstacle)
            map[y1:y2, x1:x2] = 1

        return self._with_safety_margin(map)

    def _with_safety_margin(self, map: Map) -> Map:
        kernel = self._safety_margin_kernel()
        return convolve2d(map, kernel, mode="same", boundary="fill")

    def _safety_margin_kernel(self) -> NDArray[int8]:
        radius = self.ctx.state.subdivisions * \
            SAFE_DISTANCE / self.ctx.state.physical_size

        size = int(radius * 2 + 1)
        kernel = np.zeros((size, size), dtype=np.int8)

        for i in range(size):
            for j in range(size):
                if (i - radius) ** 2 + (j - radius) ** 2 <= radius ** 2:
                    kernel[i, j] = 1

        return kernel

    def _obstacle_to_location(self, obstacle: ObstacleQuad) -> tuple[Location, Location]:
        (start, end) = obstacle
        (x1, y1) = self._to_location(start)
        (x2, y2) = self._to_location(end)
        return (x1, y1), (x2, y2)

    def _path_to_coords(self, path: list[Location]) -> list[Vec2]:
        return [self._to_coords(location) for location in path]

    def _to_location(self, coords: tuple[float, float]) -> Location:
        (x, y) = coords
        subdivs = self.ctx.state.subdivisions
        factor = subdivs / self.ctx.state.physical_size
        return clamp(int(x * factor), 0, subdivs), clamp(int(y * factor), 0, subdivs)

    def _to_coords(self, location: Location, centre=True) -> tuple[float, float]:
        (i, j) = location
        offset = 0.5 if centre else 0
        factor = self.ctx.state.physical_size / self.ctx.state.subdivisions
        return (i + offset) * factor, (j + offset) * factor


def profile_algo(
    start: Location,
    end: Location,
    algo: Algorithm
) -> tuple[list[Location] | None, float]:
    start_time = perf_counter()
    path = algo.find_path(start, end)
    end_time = perf_counter()
    return path, end_time - start_time
