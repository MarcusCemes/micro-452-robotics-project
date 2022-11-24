from app.motion_control import MotionControl


class LocalNavigation:

    async def should_freestyle(self) -> bool:
        raise Exception("Not implemented!")

    async def freestyle(self, motion_control: MotionControl) -> None:
        raise Exception("Not implemented!")
