from asyncio import Event, create_task
from time import time
from tdmclient import ClientAsync, aw
import math
import numpy as np
from tdmclient import ClientAsyncCacheNode

from app.state import state
from app.EKF import ExtendedKalmanFilter

THYMIO_TO_CM = 3.85/100  # NEEDS TO BE MODIFIED ACCORDING TO THE THYMIO


class Filtering:

    def __init__(self, node: ClientAsyncCacheNode):
        self.node = node
        self.on_update = Event()
        self.last_update = time()

        self.ekf = ExtendedKalmanFilter(0, 0, math.pi()/2)

    def __enter__(self):
        self.task = create_task(self.run())
        return self

    def __exit__(self):
        self.task.cancel()

    async def run(self):
        while True:
            await self.node.wait_for_variables({"motor.left.speed", "motor.right.speed"})
            vl = self.node.v.motor.left.speed
            vr = self.node.v.motor.right.speed

            self.predict((vl, vr))

            self.on_update.set()  # awaken the waiting state
            self.on_update.clear()

    async def wait_for_update(self):
        await self.on_update.wait()

    async def proximity_event(self):
        """This should return once the robot should enter freestyle."""
        raise Exception("Not implemented!")

    def predict(self, velocity):

        now = time()
        dt = now - self.last_update

        (vl, vr) = velocity
        self.ekf.predict_ekf(self, vl, vr, dt)

        self.last_update = now

    def update(self, pose, orientation):  # from vision
        pass


def filtering(current_state):  # current state is a class
    """    Runs the filtering pipeline once, must be called each time a state is measured

        param current_state: current state the thymio is in from vision
            containing: x position [cm], y position [cm], orientation [rad] 

        return state: estimmation of the state (is there realy an use for that?)
    """

    speedL = node["motor.left.speed"]  # in thymio units
    speedR = node["motor.right.speed"]  # in thymio units

    # speed transformation from thymio units to cm/s
    speedL = speedL * THYMIO_TO_CM
    speedR = speedR * THYMIO_TO_CM

    # blind estimation of the next state
    state.position, state.orientation = ekf.predict(
        speedL, speedR)

    # if camera reading, estimation of the next state with measurement
    pose = np.matrix([current_state.position[0],
                     current_state.position[1], current_state.orientation])

    if (pose[0] != 0 and pose[1] != 0):  # verify condition (not sure)---------------------------------------------------------------------------------------------------------------
        # update
        # send global state
    state.mark_stale()

    return state
