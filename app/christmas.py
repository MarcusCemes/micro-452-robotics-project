from app.context import Context
from app.config import DROP_SPEED, DROP_TIME

class Second_thymio(self):

    def __init__(self, ctx: Context):

        self.ctx = ctx
    
    async def drop_baulbe(self):
        # dropping
        await self.ctx.secondary_node.set_variables({"motor.left.target": [-DROP_SPEED], "motor.right.target": [-DROP_SPEED]})
        await sleep(DROP_TIME)

        # pause
        await self.ctx.secondary_node.set_variables({"motor.left.target": [0], "motor.right.target": [0]})
        await sleep(3)

        # back to position
        await self.ctx.secondary_node.set_variables({"motor.left.target": [DROP_SPEED], "motor.right.target": [DROP_SPEED]})
        await sleep(DROP_TIME)

        # stop
        await self.ctx.secondary_node.set_variables({"motor.left.target": [0], "motor.right.target": [0]})
