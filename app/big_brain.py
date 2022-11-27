
from asyncio import FIRST_COMPLETED, Event, create_task, sleep, wait

from app.config import SUBDIVISIONS, SLEEP_INTERVAL
from app.console import *
from app.context import Context
from app.filtering import Filtering
from app.global_navigation import GlobalNavigation
from app.local_navigation import LocalNavigation
from app.motion_control import MotionControl
from app.vision import Vision


class BigBrain:

    def __init__(self, ctx: Context, sleep_interval=SLEEP_INTERVAL):
        self.ctx = ctx
        self.sleep_interval = sleep_interval

    async def start_thinking(self):

        create_task(self.var_speed())
        # create_task(self.print_speed())

        await self.ctx.node.watch(variables=True)
        # await self.ctx.node.wait_for_variables({"motor.left.speed", "motor.right.speed"})

        with Filtering(self.ctx) as filtering:
            with MotionControl(self.ctx) as motion_control:
                with GlobalNavigation(self.ctx) as global_nav:
                    await self.loop(
                        Vision(),
                        filtering,
                        motion_control,
                        global_nav,
                        LocalNavigation(),
                    )

    async def var_speed(self):
        while True:
            await sleep(2)
            await self.ctx.node.set_variables(
                {"motor.left.target": [0], "motor.right.target": [0]})
            await sleep(2)
            await self.ctx.node.set_variables(
                {"motor.left.target": [100], "motor.right.target": [100]})

    async def loop(
        self,
        vision: Vision,
        filtering: Filtering,
        motion_control: MotionControl,
        global_nav: GlobalNavigation,
        local_nav: LocalNavigation,
    ):

        await Event().wait()

        while True:
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
