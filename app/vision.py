from dataclasses import dataclass
from time import time
from typing import Any

import numpy as np

from app.context import Context


@dataclass
class Frame:
    position: tuple[float, float]
    orientation: float
    obstacles: Any


class Vision():

    def __init__(self, ctx: Context):
        self.ctx = ctx
        self.last_update = time()

    def next_frame(self, subdivisions: int):
        image = self.capture_image()
        return self.process_image(image, subdivisions)

    def capture_image(self):
        # capture image
        pass

    def process_image(self, image, subdivisions) -> Frame:
        # process image
        obstacles = np.array([subdivisions, subdivisions], dtype=np.int8)
        return Frame((0, 0), 0, obstacles)
