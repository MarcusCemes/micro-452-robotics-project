import numpy as np
import math

from app.context import Context
from app.utils.module import Module
from app.utils.types import Vec2

MAX_WAIT = 0.1


class MotionControl(Module):
    def __init__(self, ctx: Context):
        super().__init__(ctx)

        self.times = 0
        self.factor = 2

        self.relative_distance = None
        self.ctx = ctx
        self.waypoint = None
        self.ctx.state.reactive_control = False

    def setNewWaypoint(self, indexMore):  # update the waypoint to go
        if self.ctx.state.next_waypoint_index is None:
            return
        if self.ctx.state.path is None:
            return

        index = min(
            self.ctx.state.next_waypoint_index + indexMore, len(self.ctx.state.path) - 1
        )

        if index == -1:  # no more path
            return
        if self.ctx.state.path[index] is None:  # not defined waypoint problem
            return

        self.waypoint = self.ctx.state.path[index]
        self.ctx.state.next_waypoint_index = index

    async def run(self):  # update function
        while True:
            await self.ctx.pose_update.wait(timeout=MAX_WAIT)
            await self.update_motor_control()  # update the control function

    def update_waypoint(self, waypoint: Vec2 | None):
        self.waypoint = waypoint

    async def update_motor_control(self):  # control function
        if self.waypoint is None:
            self.setNewWaypoint(1)
        # Compute the required motor speed to reach the next waypoint
        if self.ctx.state.reactive_control:  # choice of control (waypoint or reactive)
            (arrived, vLC, vRC) = self.controlWithDistance()  # reactive control
        else:
            controlPos = self.controlPosition()  # control by waypoint
            if controlPos is None:
                return
            (arrived, vLC, vRC) = controlPos

            if arrived:  # if arrived to the aimed waypoint update to the next one
                if self.ctx.state.next_waypoint_index is None:
                    return
                if self.ctx.state.path is None:
                    return
                self.setNewWaypoint(1)

        await self.ctx.node.set_variables(  # apply the control on the wheels
            {"motor.left.target": [int(vLC)], "motor.right.target": [int(vRC)]}
        )

    def controlPosition(self):  # PD control with Fuzzy control for the angle
        if self.ctx.state.position is None:
            return None
        if self.waypoint is None:
            return None
        if self.ctx.state.orientation is None:
            return None

        currentPos = np.array([self.ctx.state.position[0], self.ctx.state.position[1]])

        waypoint = np.array([self.waypoint[0], self.waypoint[1]])

        error = waypoint - currentPos  #

        dAngle = math.atan2(error[1], error[0]) - self.ctx.state.orientation
        dDist = min(math.sqrt(error[1] * error[1] + error[0] * error[0]), 8)
        self.ctx.state.dist = dDist

        if abs(dAngle) > math.pi:
            dAngle = -2 * np.sign(dAngle) * math.pi + dAngle

        vForward = 0
        # Fuzzy control HERE if angle > 45 degrees => just rotate do not go forward
        #                   if angle [10:45]  degrees => just rotate and move forward slowly
        #                   if angle < 10 degrees => rotate and move forward
        if abs(dAngle) < 45 * math.pi / 180:
            if abs(dAngle) < 10 * math.pi / 180:
                vForward = max(dDist, 4) * 5
            else:
                vForward = max(dDist, 4) * 1
        vAngle = dAngle * 80
        temp = abs(vAngle)
        temp = min(temp, 50)
        vAngle = temp * np.sign(vAngle)

        if abs(dDist) < 6:  # if < 6 cm of the waypoint => go to the next waypoint
            if abs(dDist) < 1:  # if < 1 cm => stop
                if (
                    self.ctx.state.next_waypoint_index
                    == len(self.ctx.state.path or []) - 1
                ):
                    self.ctx.state.arrived = True
                    return [True, 0, 0]
            return [True, vForward - vAngle, vForward + vAngle]

        return [False, vForward - vAngle, vForward + vAngle]

    def controlWithDistance(self):
        distances = np.array(self.ctx.state.relative_distances)
        bb = (
            self.controlPosition()
        )  # if arrives close to the waypoint => update the state next_waypoint
        arrived = False
        if bb is not None:
            arrived = bb[0]
        distances = np.array(self.ctx.state.relative_distances)
        vForward = 30
        vAngle = -3
        if distances[0] == -1:  # corners control
            self.times = self.times + 1 * self.factor
            if self.times < 40:
                vAngle = 0
            elif self.times < 80:
                vAngle = -4
            elif self.times < 150:
                vAngle = -8
            else:
                vAngle = -15
        # 3rd priority, if smt on the rest of the sensors
        newD = np.array([distances[1], distances[3], distances[4]])
        newD = newD[newD != -1]
        if len(newD) > 0:
            dMin = newD.min()
            if dMin < 5:
                self.times = 0
                vAngle = -(dMin - 5) * 10
                if dMin < 4:
                    vForward = (dMin - 4) * 10

        # 2nd priority, if smt on the left sensor
        if distances[0] != -1:
            self.times = 0
            if distances[0] < 5:
                vAngle = -(distances[0] - 5) * 8
                if distances[0] < 4:
                    vForward = (distances[0] - 4) * 10
        # 1st priority, if senses smt in the front sensor
        if distances[2] != -1 and distances[2] < 5:
            print("??")
            self.times = 0
            vAngle = -(distances[2] - 5) * 10
            if distances[2] < 4:
                vForward = (distances[2] - 4) * 10
        return [
            arrived,
            int((vForward + vAngle) * self.factor),
            int((vForward - vAngle) * self.factor),
        ]
