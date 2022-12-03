from asyncio import create_task
from dataclasses import dataclass
from time import perf_counter
from typing import Generator

from app.config import SUBDIVISIONS
from app.context import Context
from app.state import ExtraObstacle
from app.utils.background_task import BackgroundTask
from app.utils.types import Coords, Vec2


@dataclass
class PathFindingParams:
    start: Vec2
    end: Vec2
    obstacles: list[list[int]]
    extra_obstacles: list[ExtraObstacle]
    subdivisions: int
    physical_size: Vec2


@dataclass
class PathFindingResult:
    computation_time: float
    path: list[Vec2] | None


class GlobalNavigation(BackgroundTask):

    def __init__(self, ctx: Context):
        super().__init__()
        self.ctx = ctx

    async def run(self):
        while True:
            await self.ctx.scene_update.wait()
            await self.recompute_path()

    async def recompute_path(self):
        if not self.ctx.state.start or not self.ctx.state.end:
            return False

        params = PathFindingParams(
            end=self.ctx.state.end,
            obstacles=self.ctx.state.obstacles,
            extra_obstacles=self.ctx.state.extra_obstacles,
            physical_size=self.ctx.state.physical_size,
            start=self.ctx.state.start,
            subdivisions=self.ctx.state.subdivisions
        )

        result = await self.ctx.pool.run(find_optimal_path, params)

        self.ctx.state.path = result.path
        self.ctx.state.computation_time = result.computation_time
        self.ctx.state.changed()

        return True


def find_optimal_path(params: PathFindingParams) -> PathFindingResult:
    algo = Dijkstra(params)

    start_time = perf_counter()
    path = algo.calculate()
    end_time = perf_counter()

    return PathFindingResult(end_time - start_time, path)


@ dataclass
class Node:
    distance: float = float("inf")
    visitable: bool = True
    parent: Coords | None = None
    visited: bool = False


class Dijkstra:
    def __init__(
        self,
        params: PathFindingParams,
    ):
        self.size = params.physical_size
        self.path = None

        self.graph = Graph(SUBDIVISIONS, self.size)

        self.start = self.graph.get_index(params.start)
        self.end = self.graph.get_index(params.end)

        self.graph.node(self.start).distance = 0.0

        self.apply_obstacles(params.obstacles)
        self.apply_extra_obstacles(params.extra_obstacles)

    def apply_obstacles(self, obstacles: list[list[int]]):
        for y, row in enumerate(obstacles):
            for x, value in enumerate(row):
                coords = (x, y)
                visitable = not bool(value)
                if not visitable and self.graph.coords_in_bounds(coords):
                    self.graph.node(coords).visitable = False

    def apply_extra_obstacles(self, obstacles: list[ExtraObstacle]):
        for obstacle in obstacles:
            for coords in self.obstacle_coords(obstacle):
                self.graph.node(coords).visitable = False

    def obstacle_coords(self, obstacle: ExtraObstacle) -> Generator[Coords, None, None]:
        (x1, y1) = self.graph.get_index(obstacle[0])
        (x2, y2) = self.graph.get_index(obstacle[1])

        for x in range(x1, x2 + 1):
            for y in range(y1, y2 + 1):
                coords = (x, y)
                if self.graph.coords_in_bounds(coords):
                    yield coords

    def calculate(self) -> list[Vec2] | None:
        if self.path:
            return self.path

        queue = [self.start]
        queue_set = {self.start}

        while queue:
            visitor_coords = queue.pop(0)
            queue_set.remove(visitor_coords)

            visitor = self.graph.node(visitor_coords)
            visitor.visited = True

            if visitor_coords == self.end:
                self.path = self.calculate_path()
                return self.path

            for (coords, delta) in self.graph.neighbours(visitor_coords):
                neighbour = self.graph.node(coords)

                if (not neighbour.visitable) or neighbour.visited:
                    continue

                visitor_distance = visitor.distance + delta

                if visitor_distance < neighbour.distance:
                    neighbour.distance = visitor_distance
                    neighbour.parent = visitor_coords

                if coords not in queue_set:
                    queue.append(coords)
                    queue_set.add(coords)

                queue.sort(
                    key=lambda coords: self.graph.node(coords).distance)

        return None

    def calculate_path(self) -> list[Vec2]:
        path = []
        cursor = self.end

        while cursor:
            path.append(self.graph.get_coords(cursor))
            cursor = self.graph.node(cursor).parent

        path.reverse()
        return path


class Graph:
    def __init__(self, subdivisions: int, size: Vec2):
        self.size = size
        self.subdivisions = subdivisions
        self.nodes = [[Node() for _ in range(SUBDIVISIONS)]
                      for _ in range(SUBDIVISIONS)]

    def node(self, coords: Coords) -> Node:
        (x, y) = coords
        return self.nodes[x][y]

    def get_index(self, coords: Vec2) -> Coords:
        (x, y) = coords
        x = round(x * float(self.subdivisions) / self.size[0])
        y = round(y * float(self.subdivisions) / self.size[1])
        return (x, y)

    def get_coords(self, index: Coords) -> Vec2:
        (x, y) = index
        x = (x + 0.5) * self.size[0] / float(self.subdivisions)
        y = (y + 0.5) * self.size[1] / float(self.subdivisions)
        return (x, y)

    def coords_in_bounds(self, coords: Coords) -> bool:
        (x, y) = coords
        return 0 <= x < self.subdivisions and 0 <= y < self.subdivisions

    def neighbours(self, coords: Coords) -> Generator[tuple[Coords, float], None, None]:
        (x, y) = coords

        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue

                if 0 <= x + i < SUBDIVISIONS and 0 <= y + j < SUBDIVISIONS:
                    distance = 1 if i == 0 or j == 0 else 1.41
                    yield ((x + i, y + j), distance)
