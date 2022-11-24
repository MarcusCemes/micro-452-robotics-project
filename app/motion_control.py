
from asyncio import create_task

from app.context import Context
from app.types import Vec2


class MotionControl:

    def __init__(self, ctx: Context):
        self.ctx = ctx
        self.waypoint = None

    def __enter__(self):
        self.task = create_task(self.run())
        return self

    def __exit__(self):
        self.task.cancel()

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
