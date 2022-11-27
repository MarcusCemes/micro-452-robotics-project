import math
from asyncio import Event
from time import time

import numpy as np

from app.context import Context
from app.EKF import ExtendedKalmanFilter
from app.utils.console import *
from app.utils.event_processor import ThymioEventProcessor

THYMIO_TO_CM = 3.85e-2  # NEEDS TO BE MODIFIED ACCORDING TO THE THYMIO


class Filtering(ThymioEventProcessor):

    def __init__(self, ctx: Context):
        super().__init__(ctx)

        self.on_update = Event()
        self.last_update = time()

        self.ekf = ExtendedKalmanFilter((0, 0),  math.pi/2)

    def process_event(self, variables):
        [vl] = variables["motor.left.speed"]
        [vr] = variables["motor.right.speed"]

        self.predict(vl, vr)

        self.ctx.pose_update.trigger()
        self.ctx.state.changed()

    async def wait_for_update(self):
        await self.on_update.wait()

    async def proximity_event(self):
        """This should return once the robot should enter freestyle."""
        raise Exception("Not implemented!")

    def predict(self, vl, vr):
        now = time()
        dt = now - self.last_update

        pose_x_est, pose_y_est, orientation_est = self.ekf.predict_ekf(
            vl, vr, dt)

        self.ctx.state.position = (pose_x_est, pose_y_est)
        self.ctx.state.orientation = orientation_est

        self.last_update = now

    def update(self, pose, orientation):  # from vision
        # filter recomputation and context update
        z = np.array(pose, orientation)
        pose_x_est, pose_y_est, orientation_est = self.ekf.update_ekf(z)
        self.ctx.state.position = (pose_x_est, pose_y_est)
        self.ctx.state.orientation = orientation_est


""" def filtering(current_state):  # current state is a class
       Runs the filtering pipeline once, must be called each time a state is measured

        param current_state: current state the thymio is in from vision
            containing: x position [cm], y position [cm], orientation [rad]

        return state: estimmation of the state (is there realy an use for that?)


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
        state.changed()

    return state """
