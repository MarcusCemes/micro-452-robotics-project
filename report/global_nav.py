import matplotlib.pyplot as plt
import numpy as np

from app.config import PHYSICAL_SIZE_CM, SUBDIVISIONS
from app.context import Context


def reset(ctx: Context):
    ctx.state.boundary_map = None
    ctx.state.obstacles = np.zeros((SUBDIVISIONS, SUBDIVISIONS), dtype=np.int8)
    ctx.state.path = None
    ctx.state.position = None
    ctx.state.end = None
    ctx.state.optimise = False


def plot_map(ctx: Context):
    map = create_map(ctx)
    plt.imshow(map, cmap="YlGnBu")

    if ctx.state.position is not None:
        (y, x) = to_image_space(ctx.state.position)
        plt.plot(y, x, "ro")

    if ctx.state.end is not None:
        (y, x) = to_image_space(ctx.state.end)
        plt.plot(y, x, "co")

    if ctx.state.path is not None:
        path = np.array(ctx.state.path)
        path = np.apply_along_axis(to_image_space, 1, path)
        plt.plot(path[:, 0], path[:, 1], "g")

    plt.title("Path-finding map")
    plt.axis("off")

    # Flip the y-axis
    plt.gca().invert_yaxis()

    plt.show()


def create_map(ctx: Context):
    map = np.zeros((SUBDIVISIONS, SUBDIVISIONS))

    if ctx.state.boundary_map is not None:
        map[ctx.state.boundary_map != 0] = 128

    if ctx.state.obstacles is not None:
        map[ctx.state.obstacles != 0] = 255

    return map


def plot_raytrace(matrix, p1, p2):
    plt.imshow(matrix, cmap="YlGnBu")
    plt.plot([p1[0], p2[0]], [p1[1], p2[1]])
    plt.plot(p1[0], p1[1], "ro")
    plt.plot(p2[0], p2[1], "co")
    plt.axis("off")
    plt.title("Ray-tracing algorithm")
    plt.show()


def plot_path_optimisation(path, optimised_path, obstacles):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))

    path = np.array(path)
    optimised_path = np.array(optimised_path)

    ax1.imshow(obstacles, cmap="YlGnBu")
    ax2.imshow(obstacles, cmap="YlGnBu")

    ax1.plot(path[:, 0], path[:, 1], "g")
    ax1.plot(path[0, 0], path[0, 1], "ro")
    ax1.plot(path[-1, 0], path[-1, 1], "co")
    ax1.set_title("Original path")
    ax1.axis("off")

    ax2.plot(optimised_path[:, 0], optimised_path[:, 1], "g")
    ax2.plot(optimised_path[0, 0], optimised_path[0, 1], "ro")
    ax2.plot(optimised_path[-1, 0], optimised_path[-1, 1], "co")
    ax2.set_title("Optimised path")
    ax2.axis("off")

    plt.show()


def plot_image(image, title=None, colourbar=False):
    plt.imshow(image, cmap="YlGnBu")
    plt.axis("off")

    if colourbar:
        plt.colorbar()

    if title is not None:
        plt.title(title)

    plt.show()


def path_to_coords(path):
    factor = SUBDIVISIONS / PHYSICAL_SIZE_CM
    return [
        (int(factor * x), int(factor * y))
        for (x, y) in path
    ]


def to_image_space(coords):
    (x, y) = coords
    factor = SUBDIVISIONS / PHYSICAL_SIZE_CM
    return (x * factor, y * factor)


def to_physical_space(coords):
    (y, x) = coords
    factor = PHYSICAL_SIZE_CM / SUBDIVISIONS
    return (x * factor, y * factor)
