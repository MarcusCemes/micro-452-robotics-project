from dataclasses import dataclass

SUBDIVISIONS = 16


def idx(coords: tuple[float, float]) -> tuple[int, int]:
    (x, y) = coords
    return (round(x * SUBDIVISIONS), round(y * SUBDIVISIONS))


_start: tuple[int, int] = idx((0.2, 0.2))
_end: tuple[int, int] = idx((0.8, 0.8))

_obstacles: list[tuple[int, int]] = [idx((0.5, 0.5))]


def set_start(coords: tuple[int, int]):
    global _start
    _start = coords


def set_end(coords: tuple[int, int]):
    global _end
    _end = coords


def set_obstacles(objects: list[tuple[int, int]]):
    global _obstacles
    _obstacles = objects


async def calculate_path() -> list[tuple[int, int]]:
    matrix = create_matrix()
    matrix[_start[0]][_start[1]].distance = 0.0
    apply_obstacles(matrix)
    return djikstra(matrix)


@dataclass
class Node:
    distance: float
    obstacle: bool
    parent: tuple[int, int] | None


def create_matrix():
    return [[Node(float("inf"), False, None) for _ in range(SUBDIVISIONS)]
            for _ in range(SUBDIVISIONS)]


def apply_obstacles(matrix: list[list[Node]]):
    for obstacle in _obstacles:
        x, y = obstacle
        matrix[x][y].obstacle = True


def djikstra(matrix: list[list[Node]]):
    global _start, _end

    queue: list[tuple[int, int]] = [_start]

    while queue:
        current_coords = queue.pop(0)
        current = matrix[current_coords[0]][current_coords[1]]

        if current == _end:
            break
        for ((x, y), distance) in get_neighbours(current_coords):
            if not matrix[x][y].obstacle:
                new_distance = current.distance + distance
                if new_distance < matrix[x][y].distance:
                    matrix[x][y].distance = new_distance
                    matrix[x][y].parent = current_coords
                    queue.append((x, y))

    path = [_end]
    cursor = matrix[_end[0]][_end[1]].parent

    while cursor != None:
        path.append(cursor)
        cursor = matrix[cursor[0]][cursor[1]].parent

    return path


def get_neighbours(coords: tuple[int, int]) -> list[tuple[tuple[int, int], float]]:
    x, y = coords

    neighbours = []

    for i in range(-1, 2):
        for j in range(-1, 2):
            if i == 0 and j == 0:
                continue
            if 0 <= x + i < SUBDIVISIONS and 0 <= y + j < SUBDIVISIONS:
                distance = 1 if i == 0 or j == 0 else 1.41
                neighbours.append(((x + i, y + j), distance))

    return neighbours
