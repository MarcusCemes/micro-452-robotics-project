from app.context import Context
from app.config import DROP_SPEED, DROP_TIME, HALF_TURN_TIME, HALF_TURN_SPEED
from app.utils.console import *
from asyncio import sleep


class Christmas_celebration:

    def __init__(self, ctx: Context):

        self.ctx = ctx

    async def drop_baulbe(self):
        # dropping
        await self.ctx.node_top.set_variables({"motor.left.target": [DROP_SPEED], "motor.right.target": [DROP_SPEED]})
        await sleep(DROP_TIME)
        debug("Dropped")

        # pause
        await self.ctx.node_top.set_variables({"motor.left.target": [0], "motor.right.target": [0]})
        await sleep(3)

        # back to position
        await self.ctx.node_top.set_variables({"motor.left.target": [-DROP_SPEED], "motor.right.target": [-DROP_SPEED]})
        await sleep(DROP_TIME)

        # stop
        await self.ctx.node_top.set_variables({"motor.left.target": [0], "motor.right.target": [0]})
    
    async def do_half_turn(self):
        await self.ctx.node.set_variables({"motor.left.target": [HALF_TURN_SPEED], "motor.right.target": [-HALF_TURN_SPEED]})
        await sleep(HALF_TURN_TIME)
        await self.ctx.node.set_variables({"motor.left.target": [0], "motor.right.target": [0]})
        debug("half turn done")
    
    async def stop_thymio(self):
        await self.ctx.node.set_variables({"motor.left.target": [0], "motor.right.target": [0]})