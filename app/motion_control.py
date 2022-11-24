
from asyncio import create_task
from tdmclient import ClientAsyncCacheNode

from app.filtering import Filtering
from app.types import Vec2


class MotionControl:
    def __init__(self, node: ClientAsyncCacheNode, filtering: Filtering):
        self.node = node
        self.filtering = filtering
        self.waypoint = None

    def __enter__(self):
        self.task = create_task(self.run())
        return self

    def __exit__(self):
        self.task.cancel()

    async def run(self):
        while True:
            await self.filtering.wait_for_update()
            self.update_motor_control()

    def update_waypoint(self, waypoint: Vec2 | None):
        self.waypoint = waypoint
        self.update_motor_control()

    def update_motor_control(self):
        # TODO: Calculate the required motor speeds to reach the next waypoint
        raise Exception("Not implemented!")
