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

    def setNewWaypoint(self, indexMore):
        if self.ctx.state.next_waypoint_index is None:
            return
        if self.ctx.state.path is None:
            return

        index = min(self.ctx.state.next_waypoint_index +
                    indexMore, len(self.ctx.state.path)-1)

        # print(index)
        if (index == -1):
            return
        if self.ctx.state.path[index] is None:
            return

        self.waypoint = self.ctx.state.path[index]
        self.ctx.state.next_waypoint_index = index

    async def run(self):
        while True:
            await self.ctx.pose_update.wait(timeout=MAX_WAIT)
            await self.update_motor_control()

    def update_waypoint(self, waypoint: Vec2 | None):
        self.waypoint = waypoint

    async def update_motor_control(self):
        if self.waypoint is None:
            self.setNewWaypoint(1)

        # TODO: Calculate the required motor speeds to reach the next waypoint
        if (self.ctx.state.reactive_control):
            (arrived, vLC, vRC) = self.controlWithDistance()
        else:
            controlPos = self.controlPosition()
            if controlPos is None:
                print("out")
                return
            (arrived, vLC, vRC) = controlPos
            if arrived:
                if self.ctx.state.next_waypoint_index is None:
                    # do a 180degree turn
                    return
                if self.ctx.state.path is None:
                    return
                self.setNewWaypoint(1)

            await self.ctx.node.set_variables(
                {"motor.left.target": [int(vLC)], "motor.right.target": [int(vRC)]})

    def controlPosition(self):  # include T somewhere
        if self.ctx.state.position is None:
            return None
        if self.waypoint is None:
            return None
        if self.ctx.state.orientation is None:
            return None
        currentPos = np.array(
            [self.ctx.state.position[0], self.ctx.state.position[1]])

        waypoint = np.array([self.waypoint[0], self.waypoint[1]])

        error = waypoint-currentPos

        dAngle = math.atan2(error[1], error[0])-self.ctx.state.orientation
        dDist = min(math.sqrt(error[1]*error[1]+error[0]*error[0]), 8)
        self.ctx.state.dist = dDist

        if (abs(dAngle) > math.pi):
            dAngle = - 2*np.sign(dAngle)*math.pi + dAngle

        vForward = 0

        if (abs(dAngle) < 45*math.pi/180):
            if (abs(dAngle) < 10*math.pi/180):
                vForward = max(dDist, 4)*5
            else:
                vForward = max(dDist, 4)*1
        vAngle = dAngle*80
        temp = abs(vAngle)
        temp = min(temp, 50)
        vAngle = temp*np.sign(vAngle)

        if (abs(dDist) < 6):
            if (abs(dDist) < 1):
                    self.ctx.state.arrived = True
                    return [True, 0, 0]
            return [True, vForward-vAngle, vForward+vAngle]

        return [False, vForward-vAngle, vForward+vAngle]

    def controlWithDistance(self):
        try:
            [a,b,c] = self.controlPosition() #get update on waypoints
            distances = np.array(self.ctx.state.relative_distances)
            vForward = 30
            vAngle = -3
            if (distances[0] == -1):
                self.times = self.times+1*self.factor
                if (self.times < 40):
                    vAngle = 0
                elif (self.times < 80):
                    vAngle = -4
                elif (self.times < 150):
                    vAngle = -8
                else:
                    vAngle = -15

            # the higher the less priority you have
            newD = np.array([distances[1], distances[3], distances[4]])
            newD = newD[newD!=-1]
            if(len(newD) > 0):
                dMin = newD.min()
                if (dMin < 5):
                    self.times = 0
                    vAngle = -(dMin-5)*10
                    if(dMin < 4):
                        vForward = (dMin-4)*10

            # 2nd priority, if smt in left sensor
            if (distances[0] != -1):
                self.times = 0
                if (distances[0] < 5):
                    vAngle = -(distances[0]-5)*8
                    if (distances[0] < 4):
                        vForward = (distances[0]-4)*10
            # 1st priority, if sens smt in front stop
            if (distances[2] != -1 and distances[2] < 5):
                self.times = 0
                vAngle = -(distances[2]-5)*10
                if (distances[2] < 4):
                    vForward = (distances[2]-4)*10

            return [False, int((vForward + vAngle)*self.factor), int((vForward - vAngle)*self.factor)]
        except:
            print("The Thymio hasn't sent any prox sensors impules before")
            return [False, 0, 0]
