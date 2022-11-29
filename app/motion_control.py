
from asyncio import create_task
import numpy as np
import math

from app.context import Context
from app.utils.background_task import BackgroundTask
from app.utils.types import Vec2


class MotionControl(BackgroundTask):

    def __init__(self, ctx: Context):
        super().__init__()

        self.times = 0
        self.factor = 2

        self.relative_distance = None
        self.ctx = ctx
        self.waypoint = None

    def update_waypoint(self, waypoint: Vec2 | None):
        self.waypoint = waypoint

    async def update_motor_control(self):
        #print("Update Motor called :)")
        # TODO: Calculate the required motor speeds to reach the next waypoint
        if (self.ctx.state.reactive_control):
            #print("You doing good baby")
            (arrived, vLC, vRC) = self.controlWithDistance()
        else:
            (arrived, vLC, vRC) = self.controlPosition()

        #print(vLC, vRC)
        await self.ctx.node.set_variables(
            {"motor.left.target": [vLC], "motor.right.target": [vRC]})

        #raise Exception("Not implemented!")

    def controlPosition(self):  # include T somewhere
        currentposition = np.array(
            [self.ctx.state.position]+[self.ctx.state.orientation])
        waypoint = np.array(self.waypoint)

        error = waypoint-currentposition

        dAngle = math.atan2(error[1], error[0])-currentposition[2]
        dDist = math.sqrt(error[1]*error[1]+error[0]*error[0])

        if (abs(dAngle) > math.pi):
            dAngle = - 2*np.sign(dAngle)*math.pi + dAngle

        vForward = 0

        if (abs(dAngle) < 10*math.pi/180):
            vForward = dDist*5
        vAngle = dAngle*80
        temp = abs(vAngle)
        temp = min(temp, 80)
        vAngle = temp*np.sign(vAngle)

        if (abs(dAngle) < 0.1 and abs(dDist) < 0.3):
            return [True, 0, 0]

        return [False, vForward+vAngle, vForward-vAngle]

    def controlWithDistance(self):
        distances = np.array(self.ctx.state.relative_distances)
        #print("Coucou :)", distances)
        vForward = 20
        vAngle = -3

        if (distances[0] == -1):
            # print(self.times)
            self.times = self.times+1*self.factor
            if (self.times < 40):
                vAngle = 0
            elif (self.times < 80):
                vAngle = -4
            elif (self.times < 150):
                vAngle = -8
            else:
                vAngle = -15

        if (distances[4] != -1 and distances[4] < 4):
            #print("prox droite ")
            pass

        if (distances[0] != -1):
            self.times = 0
            if (distances[0] < 6):
                vAngle = -(distances[0]-6)*5
                if (distances[0] < 4):
                    vForward = (distances[0]-4)*20

        if (distances[2] != -1 and distances[2] < 5):
            self.times = 0
            vAngle = -(distances[2]-5)*10
            if (distances[2] < 4):
                vForward = (distances[2]-4)*20

        return [False, int((vForward + vAngle)*self.factor), int((vForward - vAngle)*self.factor)]
