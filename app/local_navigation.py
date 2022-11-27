from app.context import Context
from app.motion_control import MotionControl


class LocalNavigation:

    def __init__(self, ctx: Context):
        self.ctx = ctx

    async def should_freestyle(self) -> bool:
        raise Exception("Not implemented!")

    async def freestyle(self, motion_control: MotionControl) -> None:
        raise Exception("Not implemented!")
