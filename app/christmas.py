from app.context import Context
from app.config import DROP_SPEED, DROP_TIME
from app.utils.console import *
from asyncio import sleep


class Second_thymio:

    def __init__(self, ctx: Context):

        self.ctx = ctx

    async def drop_baulbe(self):
        # dropping
        await self.ctx.node_top.set_variables({"motor.left.target": [DROP_SPEED], "motor.right.target": [DROP_SPEED]})
        await sleep(DROP_TIME)

        # pause
        await self.ctx.node_top.set_variables({"motor.left.target": [0], "motor.right.target": [0]})
        await sleep(3)

        # back to position
        await self.ctx.node_top.set_variables({"motor.left.target": [-DROP_SPEED], "motor.right.target": [-DROP_SPEED]})
        await sleep(DROP_TIME)

        # stop
        await self.ctx.node_top.set_variables({"motor.left.target": [0], "motor.right.target": [0]})
