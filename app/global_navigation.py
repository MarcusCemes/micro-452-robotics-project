from dataclasses import dataclass
from time import perf_counter
from typing import Generator
from app.parallel import Pool

from app.state import State, state

SUBDIVISIONS = 64

IntVec2 = tuple[int, int]
FloatVec2 = tuple[float, float]


async def recompute_path():
    (path, time) = await Pool().run(find_optimal_path, state)
    state.path = path
    state.computation_time = time
    state.mark_stale()


def find_optimal_path(state: State) -> tuple[list[FloatVec2] | None, float]:
    algo = Dijkstra(state)

    start_time = perf_counter()
    path = algo.calculate()
    end_time = perf_counter()

    return (path, end_time - start_time)


@dataclass
class Node:
    distance: float = float("inf")
    visitable: bool = True
    parent: IntVec2 | None = None
    visited: bool = False


class Dijkstra:
    def __init__(
        self,
        state: State,
    ):
        self.graph = Graph(SUBDIVISIONS, state.physical_size)
        self.path = None

        self.start = self.graph.get_index(state.start)
        self.end = self.graph.get_index(state.end)
        self.size = state.physical_size

        self.graph.node(self.start).distance = 0.0

        self.apply_obstacles(state.obstacles)

    def apply_obstacles(self, obstacles: list[tuple[FloatVec2, FloatVec2]]):
        for (start, end) in obstacles:
            start = self.graph.get_index(start)
            end = self.graph.get_index(end)

            for x in range(start[0], end[0] + 1):
                for y in range(start[1], end[1] + 1):
                    self.graph.node((x, y)).visitable = False

    def calculate(self) -> list[FloatVec2] | None:

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

    def calculate_path(self) -> list[FloatVec2]:
        path = []
        cursor = self.end

        while cursor:
            path.append(self.graph.get_coords(cursor))
            cursor = self.graph.node(cursor).parent

        path.reverse()
        return path


class Graph:
    def __init__(self, subdivisions: int, size: FloatVec2):
        self.size = size
        self.subdivisions = subdivisions
        self.nodes = [[Node() for _ in range(SUBDIVISIONS)]
                      for _ in range(SUBDIVISIONS)]

    def node(self, coords: IntVec2) -> Node:
        (x, y) = coords
        return self.nodes[x][y]

    def get_index(self, coords: FloatVec2) -> IntVec2:
        (x, y) = coords
        x = round(x * float(self.subdivisions) / self.size[0])
        y = round(y * float(self.subdivisions) / self.size[1])
        return (x, y)

    def get_coords(self, index: IntVec2) -> FloatVec2:
        (x, y) = index
        x *= self.size[0] / float(self.subdivisions)
        y *= self.size[1] / float(self.subdivisions)
        return (x, y)

    def neighbours(self, coords: IntVec2) -> Generator[tuple[IntVec2, float], None, None]:
        (x, y) = coords

        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue

                if 0 <= x + i < SUBDIVISIONS and 0 <= y + j < SUBDIVISIONS:
                    distance = 1 if i == 0 or j == 0 else 1.41
                    yield ((x + i, y + j), distance)
