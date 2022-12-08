import math
from asyncio import Event
from time import time

import numpy as np

from app.context import Context
from app.EKF import ExtendedKalmanFilter
from app.utils.console import *
from app.utils.event_processor import ThymioEventProcessor
from app.config import THYMIO_TO_CM, DT_THRESHOLD, PHYSICAL_SIZE_CM


class Filtering(ThymioEventProcessor):

    def __init__(self, ctx: Context):
        super().__init__(ctx)

        self.on_update = Event()
        self.last_update = None

        self.ekf = ExtendedKalmanFilter(
            (PHYSICAL_SIZE_CM/2, PHYSICAL_SIZE_CM/2),  math.pi)

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

        debug("predict")

        if self.last_update is None:
            self.last_update = time()
            return

        # solution bricolage
        # if self.predict_counter == 0:
        # self.last_update = time()
        now = time()
        dt = now - self.last_update

        # print("prediction number: " + str(self.predict_counter))
        # print(" dt = " + str(dt))
        # debug(f"Update number: {self.predict_counter}")
        # if dt>DT_THRESHOLD:
        #   return

        pose_x_est, pose_y_est, orientation_est = self.ekf.predict_ekf(
            vl, vr, dt)

        self.ctx.state.position = (pose_x_est, pose_y_est)
        self.ctx.state.orientation = orientation_est

        self.last_update = now
        # self.predict_counter += 1

        # print("x = " + str(pose_x_est) + " y =" + str(pose_y_est))

    def update(self, pose):  # from vision
        debug("👮‍♂️ Bad man! Called updated, don't do that!")
        # filter recomputation and context update

        self.ekf.predict_ekf(0,0,0.01)

        z = np.array([pose])
        pose_x_est, pose_y_est, orientation_est = self.ekf.update_ekf(z)
        self.ctx.state.position = (float(pose_x_est), float(pose_y_est))
        self.ctx.state.orientation = float(orientation_est)
