from asyncio import sleep

from app.config import DROP_SPEED, DROP_TIME, HALF_TURN_SPEED, HALF_TURN_TIME
from app.context import Context
from app.utils.console import *

WAIT_TIME = 3


class ChristmasCelebration:
    """A class to handle the Christmas celebration once the destination is reached."""

    def __init__(self, ctx: Context):
        self.ctx = ctx

    async def drop_bauble(self):
        """Signal the top Thymio to drop the bauble"""

        # Drop the bauble
        await self._set_arm_speed(DROP_SPEED)
        await sleep(DROP_TIME)

        # Stop moving
        await self._set_arm_speed(0)
        await sleep(WAIT_TIME)

        # Return back to the initial position
        await self._set_arm_speed(-DROP_SPEED)
        await sleep(DROP_TIME)

        # Stop moving
        await self._set_arm_speed(0)

    async def do_half_turn(self):
        await self._set_rotate_speed(HALF_TURN_SPEED)
        await sleep(HALF_TURN_TIME)
        await self._set_rotate_speed(0)

    async def stop_thymio(self):
        await self._set_rotate_speed(0)

    async def _set_arm_speed(self, speed):
        if self.ctx.node_top is None:
            return

        await self.ctx.node_top.set_variables(
            {"motor.left.target": [speed], "motor.right.target": [speed]}
        )

    async def _set_rotate_speed(self, speed):
        await self.ctx.node.set_variables(
            {"motor.left.target": [speed], "motor.right.target": [-speed]}
        )
