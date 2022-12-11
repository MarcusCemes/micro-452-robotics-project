
import math
from asyncio import sleep
from dataclasses import dataclass

import numpy as np

from app.christmas import Christmas_celebration
from app.config import *
from app.context import Context
from app.filtering import Filtering
from app.global_navigation import GlobalNavigation
from app.local_navigation import LocalNavigation
from app.motion_control import MotionControl
from app.path_finding.types import Map
from app.utils.console import *
from app.utils.outlier_rejecter import OutlierRejecter
from app.utils.types import Channel, Vec2
from app.vision import Vision

POSITION_THRESHOLD = 0.5


@dataclass
class Modules:
    """A class to hold all the modules"""

    filtering: Filtering
    global_nav: GlobalNavigation
    local_nav: LocalNavigation
    motion_control: MotionControl
    vision: Vision


class BigBrain:

    def __init__(self, ctx: Context, sleep_interval=SLEEP_INTERVAL):
        self.ctx = ctx
        self.sleep_interval = sleep_interval
        self.christmas_celebration = Christmas_celebration(ctx)

    async def start_thinking(self, rx_pos: Channel[Vec2]):
        self.init()

        modules = self.init_modules(rx_pos)

        with modules.vision:
            modules.vision.calibrate()

            with modules.filtering, \
                    modules.motion_control, \
                    modules.global_nav, \
                    modules.local_nav:

                await self.loop(modules)

    def init(self):
        """Initialise the big brain"""

        self.stop_requested = False

        # Initialise the obstacle NDArray
        subdivs = self.ctx.state.subdivisions
        self.ctx.state.obstacles = np.zeros((subdivs, subdivs), dtype=np.int8)

    def init_modules(self, rx_pos: Channel[Vec2]):
        """Initialise the modules"""

        filtering = Filtering(self.ctx, rx_pos)
        global_nav = GlobalNavigation(self.ctx)
        motion_control = MotionControl(self.ctx)
        local_nav = LocalNavigation(self.ctx, motion_control)
        vision = Vision(self.ctx)

        return Modules(filtering, global_nav, local_nav, motion_control, vision)

    async def loop(self, modules: Modules):

        back_rejecter = OutlierRejecter[Vec2](2, 5)
        front_rejecter = OutlierRejecter[Vec2](2, 5)
        orientation_rejecter = OutlierRejecter[float](0.1, 5)

        while True:
            obs = modules.vision.next()

            if obs:
                obs_orientation = self._angle(obs.back, obs.front)

                back, back_updated = back_rejecter.next(obs.back)
                front, front_updated = front_rejecter.next(obs.front)
                orientation, orientation_updated = orientation_rejecter.next(
                    obs_orientation)

                # print("orientation from state: " + str(self.ctx.state.orientation))
                # print("orientation from camera: " + str(orientation))

                # modules.filtering.update(
                # (obs.back[0], obs.back[1], orientation))
                # orientation = self.ctx.state.orientation if self.ctx.state.orientation != None else obs_orientation

                # if obs.back != (0.0, 0.0) and obs.front != (0.0, 0.0) and USE_EXTERNAL_CAMERA == True:

                if USE_LIVE_CAMERA or self.ctx.state.position == None:
                    modules.filtering.update(
                        (obs.back[0], obs.back[1], orientation))

                self.ctx.state.last_detection = back
                self.ctx.state.last_detection_2 = front
                self.ctx.state.last_orientation = orientation
                self.ctx.state.changed()

                if self.significant_change(obs.obstacles):
                    # update filtering with camera reading

                    self.ctx.state.obstacles = obs.obstacles
                    self.ctx.scene_update.trigger()

            if self.ctx.state.arrived == True:
                await self.christmas_celebration.stop_thymio()
                self.ctx.state.end = None
                self.ctx.state.path = None
                self.ctx.state.arrived = False
                self.ctx.state.changed()
                await self.christmas_celebration.do_half_turn()
                if self.ctx.node_top != None:
                    await self.christmas_celebration.drop_baulbe()
            self.ctx.debug_update = False
            await sleep(UPDATE_FREQUENCY)

    def _angle(self, p1: Vec2, p2: Vec2) -> float:
        """Returns the angle of the vector between two points in radians."""

        return math.atan2(p2[1]-p1[1], p2[0]-p1[0])

    def significant_change(self, obstacles: Map, threshold=SCENE_THRESHOLD) -> bool:
        """
        Returns true if the scene has changed significantly. This is gauged by the
        amount of changes in the obstacles matrix. If this exceeds a set threshold,
        the scene is considered to have changed significantly.
        """

        if self.ctx.state.obstacles is None:
            return False

        return self.matrix_distance(self.ctx.state.obstacles, obstacles) > threshold

    def matrix_distance(self, a: Map, b: Map) -> int:
        """Returns the L1 distance between two matrices of the same size"""
        return np.sum(np.sum(np.abs(b - a)))
