from asyncio import create_task
from dataclasses import dataclass
from time import perf_counter
from typing import Generator

from app.config import SUBDIVISIONS
from app.context import Context
from app.utils.types import Coords, Vec2


@dataclass
class PathFindingParams:
    start: Vec2
    end: Vec2
    obstacles: list[Coords]
    subdivision: int
    physical_size: Vec2


@dataclass
class PathFindingResult:
    computation_time: float
    path: list[Vec2] | None


class GlobalNavigation:

    def __init__(self, ctx: Context):
        self.ctx = ctx

    def __enter__(self):
        self.task = create_task(self.run())
        return self

    def __exit__(self, *_):
        self.task.cancel()

    async def run(self):
        while True:
            await self.ctx.scene_update.wait()
            await self.recompute_path()

    async def recompute_path(self):
        if not self.ctx.state.start or not self.ctx.state.end:
            return False

        params = PathFindingParams(
            **self.ctx.__dict__, subdivision=SUBDIVISIONS)

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


@dataclass
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

    def apply_obstacles(self, obstacles: list[Coords]):
        for coords in obstacles:
            self.graph.node(coords).visitable = False

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
        x *= self.size[0] / float(self.subdivisions)
        y *= self.size[1] / float(self.subdivisions)
        return (x, y)

    def neighbours(self, coords: Coords) -> Generator[tuple[Coords, float], None, None]:
        (x, y) = coords

        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue

                if 0 <= x + i < SUBDIVISIONS and 0 <= y + j < SUBDIVISIONS:
                    distance = 1 if i == 0 or j == 0 else 1.41
                    yield ((x + i, y + j), distance)
