
from asyncio import FIRST_COMPLETED, Event, create_task, sleep, wait

import numpy as np
import numpy.typing as npt

from app.config import (SCENE_THRESHOLD, SLEEP_INTERVAL, SUBDIVISIONS,
                        USE_EXTERNAL_CAMERA, USE_LIVE_CAMERA)
from app.context import Context
from app.filtering import Filtering
from app.global_navigation import GlobalNavigation
from app.local_navigation import LocalNavigation
from app.motion_control import MotionControl
from app.path_finding.types import Map
from app.server import setFilteringModule
from app.utils.console import *
from app.vision import Vision
from app.christmas import Second_thymio

class BigBrain:

    def __init__(self, ctx: Context, sleep_interval=SLEEP_INTERVAL):
        self.ctx = ctx
        self.sleep_interval = sleep_interval
        self.second_thymio = Second_thymio(ctx)

    async def start_thinking(self):
        self.init()

        # create_task(self.do_pings())
        # create_task(self.do_start_stop())
        # create_task(self.update_scene())

        with Filtering(self.ctx) as filtering, \
                MotionControl(self.ctx) as motion_control, \
                GlobalNavigation(self.ctx) as global_nav, \
                LocalNavigation(self.ctx, motion_control) as local_nav:

            await self.loop(
                Vision(self.ctx, external=USE_EXTERNAL_CAMERA,
                       live=USE_LIVE_CAMERA),
                filtering,
                motion_control,
                global_nav,
                local_nav,
            )

    def init(self):
        # Initialise the obstacle array
        subdivs = self.ctx.state.subdivisions
        self.ctx.state.obstacles = np.zeros((subdivs, subdivs), dtype=np.int8)

    async def do_pings(self):
        while True:
            await sleep(1)
            print("🏓 ping")

    async def do_start_stop(self):
        try:
            while True:
                await sleep(2)
                # await self.ctx.node.set_variables(
                #    {"motor.left.target": [0], "motor.right.target": [0]})
                # await sleep(2)
                await self.ctx.node.set_variables(
                    {"motor.left.target": [100], "motor.right.target": [100]})
                await self.ctx.secondary_node.set_variables(
                    {"motor.left.target": [-100], "motor.right.target": [100]})

        except Exception:
            pass

    async def update_scene(self):
        while True:
            self.ctx.scene_update.trigger()
            await sleep(1)

    async def loop(
        self,
        vision: Vision,
        filtering: Filtering,
        motion_control: MotionControl,
        global_nav: GlobalNavigation,
        local_nav: LocalNavigation,
    ):
        setFilteringModule(filtering)

        vision.calibrate()

        while True:
            obstacles, posImg, posPhy = vision.update()

            # obstacles[:][:] = 0

            if self.significant_change(obstacles):
                debug("\\[big brain] Scene changed significantly, updating")
                # update filtering with camera reading
                # filtering.update(posPhy)

                self.ctx.state.obstacles = obstacles.tolist()
                self.ctx.state.changed()
                self.ctx.scene_update.trigger()

            if self.ctx.state.arrived == True:
                await self.second_thymio.drop_baulbe()
                self.ctx.state.arrived == False

            await sleep(1)

        while True:

            if not local_nav.should_freestyle():
                await sleep(0.1)
                continue

            # print("entering freestyle 💃🕺")
            await local_nav.freestyle()
            await motion_control.update_motor_control()
            continue

            frame = vision.next_frame(SUBDIVISIONS)

            # TODO: Update state with obstacles
            self.ctx.scene_update.trigger()

            # filtering.update(frame.position, frame.orientation)

            # await self.sleep_until_event(filtering)

            if local_nav.should_freestyle():
                await local_nav.freestyle(motion_control)

    async def sleep_until_event(self, filtering: Filtering):
        """Return once something important happens, such as a proximity event."""

        await wait([
            sleep(self.sleep_interval),
            filtering.proximity_event()
        ], return_when=FIRST_COMPLETED)

    def significant_change(self, obstacles: Map) -> bool:
        if self.ctx.state.obstacles is None:
            return False

        return self.matrix_distance(self.ctx.state.obstacles, obstacles) > SCENE_THRESHOLD

    def matrix_distance(self, a: Map, b: Map) -> int:
        return np.sum(np.sum(np.abs(b - a)))
