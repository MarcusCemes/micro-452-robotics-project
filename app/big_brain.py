
from asyncio import FIRST_COMPLETED, sleep, wait
from tdmclient import ClientAsyncCacheNode

from app.config import SUBDIVISIONS, SLEEP_INTERVAL
from app.filtering import Filtering
from app.global_navigation import GlobalNavigation
from app.local_navigation import LocalNavigation
from app.motion_control import MotionControl
from app.vision import Vision


class BigBrain:

    def __init__(self, node: ClientAsyncCacheNode, sleep_interval=SLEEP_INTERVAL):
        self.node = node
        self.sleep_interval = sleep_interval

    async def start_thinking(self):
        vision = Vision()

        with Filtering(self.node) as filtering:
            with MotionControl(self.node, filtering) as motion_control:
                await self.loop(
                    vision,
                    filtering,
                    motion_control,
                    GlobalNavigation(),
                    LocalNavigation(),
                )

    async def loop(
        self,
        vision: Vision,
        filtering: Filtering,
        motion_control: MotionControl,
        global_nav: GlobalNavigation,
        local_nav: LocalNavigation,
    ):
        while True:
            frame = vision.next_frame(SUBDIVISIONS)
            global_nav.update_obstacles(frame.obstacles)
            filtering.update(frame.position, frame.orientation)

            await self.sleep_until_event(filtering)

            if local_nav.should_freestyle():
                await local_nav.freestyle(motion_control)

    async def sleep_until_event(self, filtering: Filtering):
        """Return once something import happens, such as a proximity event."""

        await wait([
            sleep(self.sleep_interval),
            filtering.proximity_event()
        ], return_when=FIRST_COMPLETED)
