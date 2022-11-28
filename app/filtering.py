import traceback

from asyncio import Event, create_task, sleep
from time import time
import math
import numpy as np
from app.context import Context

from app.console import *
from app.EKF import ExtendedKalmanFilter
from app.config import THYMIO_TO_CM


class Filtering:

    def __init__(self, ctx: Context):
        self.ctx = ctx

        self.on_update = Event()
        self.last_update = time()
        self.predict_counter = 0

        self.ekf = ExtendedKalmanFilter((0, 0),  math.pi/2)

    def __enter__(self):
        # self.task = create_task(self.run())
        debug("enter")
        self.listener = self.ctx.node.add_variables_changed_listener(
            self.on_variables_changed)
        return self

    def __exit__(self, *_):
        # self.task.cancel()
        self.ctx.node.remove_variables_changed_listener(self.listener)

    def on_variables_changed(self, _node, variables):
        try:
            [vl] = variables["motor.left.speed"]
            [vr] = variables["motor.right.speed"]

            vl = vl * THYMIO_TO_CM
            vr = vr * THYMIO_TO_CM

            # await node.wait_for_variables({"motor.left.speed", "motor.right.speed"})
            # node.watch
            # await sleep(0.1)
            # debug("Got them!")
            # debug("Got new motor speeds")
            # vl = node.v.motor.left.speed
            # vr = node.v.motor.right.speed

            self.predict(vl, vr)
            # debug("Predicted new position")
            self.ctx.pose_update.trigger()
            self.ctx.state.changed()

        except KeyError:  # if no change in motor speed, pass
            pass

        except KeyboardInterrupt as e:
            raise e

        except Exception:
            debug("Problem!")
            print(traceback.format_exc())

    async def wait_for_update(self):
        await self.on_update.wait()

    async def proximity_event(self):
        """This should return once the robot should enter freestyle."""
        raise Exception("Not implemented!")

    def predict(self, vl, vr):
        
        #solution bricolage 
        if self.predict_counter == 0:
            self.last_update = time()

        now = time()
        dt = now - self.last_update
        print("prediction number: " + str(self.predict_counter))
        #print(" dt = " + str(dt))

        pose_x_est, pose_y_est, orientation_est = self.ekf.predict_ekf(
            vl, vr, dt)


        self.ctx.state.position = (pose_x_est, pose_y_est)
        self.ctx.state.orientation = orientation_est

        self.last_update = now
        self.predict_counter += 1

        print("x = " + str(pose_x_est) + " y =" + str(pose_y_est))

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
