
from asyncio import create_task

from app.context import Context
from app.utils.background_task import BackgroundTask
from app.utils.types import Vec2


class MotionControl(BackgroundTask):

    def __init__(self, ctx: Context):
        super().__init__()

        self.ctx = ctx
        self.waypoint = None

    async def run(self):
        while True:
            await self.ctx.pose_update.wait()
            self.update_motor_control()

    def update_waypoint(self, waypoint: Vec2 | None):
        self.waypoint = waypoint
        self.update_motor_control()

    def update_motor_control(self):
        # TODO: Calculate the required motor speeds to reach the next waypoint
        raise Exception("Not implemented!")
