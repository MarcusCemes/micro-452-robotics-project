import math

from rich.console import Console
from rich.table import Table

from app.utils.types import Vec2


def stop_movement_simulation(filtering):
    filtering.process_event(
        {"motor.left.speed": [0], "motor.right.speed": [0]})


def start_movement_simulation(filtering):
    stop_movement_simulation(filtering)
    stop_movement_simulation(filtering)


def print_pose(ctx):
    table = Table(title="Thymio pose")

    table.add_column("Position")
    table.add_column("Orientation")

    table.add_row(f"{ctx.state.position}",
                  "{:.2f}".format(ctx.state.orientation))

    console = Console()
    console.print(table)


def angle(p1: Vec2, p2: Vec2) -> float:
    """Returns the angle of the vector between two points in radians."""

    return math.atan2(p2[1]-p1[1], p2[0]-p1[0])
