import math
from time import time
import numpy as np

from app.config import PHYSICAL_SIZE_CM, THYMIO_TO_CM
from app.context import Context
from app.EKF import ExtendedKalmanFilter
from app.utils.module import Module
from app.utils.types import Channel, Vec2


class Filtering(Module):

    def __init__(self, ctx: Context, rx_pos: Channel[Vec2] | None = None):
        super().__init__(ctx)

        self.rx_pos = rx_pos

        self.last_update = None

        # initial position of the thymio if no vision, middle, facing north
        self.ekf = ExtendedKalmanFilter(
            (PHYSICAL_SIZE_CM/2, PHYSICAL_SIZE_CM/2),  math.pi/2)

    async def run(self):
        if self.rx_pos is None:
            return

        while True:
            match await self.rx_pos.recv():
                case (x, y):
                    self.update((x, y, 0.0))

    def process_event(self, variables):
        """
        When variables from sensors are updated, estimate position

        param: variables from Thymio censors
        """
        [vl] = variables["motor.left.speed"]
        [vr] = variables["motor.right.speed"]

        vl = vl * THYMIO_TO_CM
        vr = vr * THYMIO_TO_CM

        self.predict(vl, vr)

        self.ctx.pose_update.trigger()
        self.ctx.state.changed()

    def predict(self, vl, vr):
        """ 
        Predicts the next position of the thymio and updates the state

        param vl: left wheel speed sensor in cm/s
        param vr: right wheel speed sensor in cm/s
        """
        if self.last_update is None:
            self.last_update = time()
            return

        now = time()
        dt = now - self.last_update

        pose_x_est, pose_y_est, orientation_est = self.ekf.predict_ekf(
            vl, vr, dt)

        self.ctx.state.position = (pose_x_est, pose_y_est)
        self.ctx.state.orientation = orientation_est

        self.last_update = now

    def update(self, pose):
        """ 
        Updates the thymio position by correcting the predictions and updating the state

        param vl: left wheel speed sensor in cm/s
        param vr: right wheel speed sensor in cm/s
        """
        self.ekf.predict_ekf(0, 0, 0.01)

        z = np.array([pose])

        pose_x_est, pose_y_est, orientation_est = self.ekf.update_ekf(z)

        self.ctx.state.position = (float(pose_x_est), float(pose_y_est))
        self.ctx.state.orientation = float(orientation_est)
