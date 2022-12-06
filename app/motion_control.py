import numpy as np
import math

from app.context import Context
from app.utils.background_task import BackgroundTask
from app.utils.types import Vec2

MAX_WAIT = 0.1


class MotionControl(BackgroundTask):

    def __init__(self, ctx: Context):
        super().__init__()

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
        if self.ctx.state.next_waypoint_index == len(self.ctx.state.path)-1:
            print("arrived")
            self.ctx.state.arrived = True
            return
        
        index = min(self.ctx.state.next_waypoint_index +
                    indexMore, len(self.ctx.state.path)-1)

        print(index)
        if (index == -1):
            print("cant go further")
            return
        if self.ctx.state.path[index] is None:
            print("is OUT")
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
            print("is null")
            self.setNewWaypoint(1)

        # TODO: Calculate the required motor speeds to reach the next waypoint
        if (self.ctx.state.reactive_control):
            (arrived, vLC, vRC) = self.controlWithDistance()
        else:
            controlPos = self.controlPosition()
            if controlPos is None:
                return
            (arrived, vLC, vRC) = controlPos
            if arrived:
                if self.ctx.state.next_waypoint_index is None:
                    # do a 180degree turn
                    return
                if self.ctx.state.path is None:
                    return
                print("next waypoint update")
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

        if (abs(dAngle) < 10*math.pi/180):
            vForward = max(dDist, 4)*5
        vAngle = dAngle*80
        temp = abs(vAngle)
        temp = min(temp, 50)
        vAngle = temp*np.sign(vAngle)

        if (abs(dDist) < 6):
            if (abs(dDist) < 1):
                return [True, 0, 0]
            return [True, vForward-vAngle, vForward+vAngle]

        return [False, vForward-vAngle, vForward+vAngle]

    def controlWithDistance(self):
        distances = np.array(self.ctx.state.relative_distances)
        vForward = 20
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
        idx = newD.argmin()
        if (newD[idx] != -1 and newD[idx] < 4):
            self.times = 0
            vAngle = -(newD[idx]-4)*10
            vForward = (newD[idx]-4)*20

        # 2nd priority, if smt in left sensor
        if (distances[0] != -1):
            self.times = 0
            if (distances[0] < 5):
                vAngle = -(distances[0]-5)*8
                if (distances[0] < 4):
                    vForward = (distances[0]-4)*20
        # 1st priority, if sens smt in front stop
        if (distances[2] != -1 and distances[2] < 5):
            self.times = 0
            vAngle = -(distances[2]-5)*10
            if (distances[2] < 4):
                vForward = (distances[2]-4)*20

        return [False, int((vForward + vAngle)*self.factor), int((vForward - vAngle)*self.factor)]
