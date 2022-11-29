
from asyncio import FIRST_COMPLETED, Event, create_task, sleep, wait

from app.config import SLEEP_INTERVAL, SUBDIVISIONS
from app.context import Context
from app.filtering import Filtering
from app.global_navigation import GlobalNavigation
from app.local_navigation import LocalNavigation
from app.motion_control import MotionControl
from app.utils.console import *
from app.vision import Vision


class BigBrain:

    def __init__(self, ctx: Context, sleep_interval=SLEEP_INTERVAL):
        self.ctx = ctx
        self.sleep_interval = sleep_interval

    async def start_thinking(self):

        # create_task(self.do_pings())
        # create_task(self.do_start_stop())

        with Filtering(self.ctx) as filtering, \
                MotionControl(self.ctx) as motion_control, \
                GlobalNavigation(self.ctx) as global_nav, \
                LocalNavigation(self.ctx) as local_nav:

            await self.loop(
                Vision(self.ctx, False),
                filtering,
                motion_control,
                global_nav,
                local_nav,
            )

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

        except Exception:
            pass

    async def loop(
        self,
        vision: Vision,
        filtering: Filtering,
        motion_control: MotionControl,
        global_nav: GlobalNavigation,
        local_nav: LocalNavigation,
    ):

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
