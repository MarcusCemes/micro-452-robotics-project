from asyncio import sleep
from typing import Any
import numpy as np
import math
from time import time

from app.context import Context
from app.motion_control import MotionControl
from app.config import PIXELS_PER_CM
from app.utils.module import Module

SLEEP_DURATION = 0.5

# Thymio characteristics
center_offset = np.array([5.5, 5.5])

sensor_pos_from_center = (
    np.array(
        [
            [0.9, 9.4],
            [3.1, 10.5],
            [5.5, 11.0],
            [8.0, 10.4],
            [10.2, 9.3],
            [8.5, 0],
            [2.5, 0],
        ]
    )
    - center_offset
)

# Each sensor have their own scale eg : [1[cm] <=> 4771 [sensor value]]
SensorsValuesFront = np.array(
    [
        [1, 4500],
        [2, 4300],
        [3, 4200],
        [4, 4100],
        [5, 3720],
        [6, 3383],
        [7, 3100],
        [8, 2827],
        [9, 2600],
        [10, 2400],
        [11, 2116],
    ]
)
SensorsValuesDiag = np.array(
    [
        [1, 4200],
        [2, 4200],
        [3, 4000],
        [4, 3900],
        [5, 3909],
        [6, 3547],
        [7, 3254],
        [8, 3008],
        [9, 2745],
        [10, 2500],
        [11, 2250],
    ]
)
SensorsValuesBack = np.array(
    [
        [1, 4992],
        [2, 4929],
        [3, 4762],
        [4, 4276],
        [5, 3744],
        [6, 3319],
        [7, 2977],
        [8, 2716],
        [9, 2489],
        [10, 2279],
        [11, 2072],
    ]
)


class LocalNavigation(Module):
    """Module that is tasked with reactive obstacle avoidance."""

    def __init__(self, ctx: Context, motion_control: MotionControl):
        super().__init__(ctx)
        self.motion_control = motion_control

        self.last_time = time()
        self.computedOnce = False

    # == Implemented methods == #

    def process_event(
        self, variables: dict[str, Any]
    ):  # Function called everytime the Thymio reads new sensors values

        self.ctx.state.prox_sensors = variables["prox.horizontal"]
        self.ctx.state.changed()  # trigger the signal to wake up other coroutines if needed

        self.update()  # this function updates the state variable : relative_distance
        self.should_freestyle()  # this function chooses the type of control

    async def run(self):
        # Sometimes the thymio doesn't send any new sensor value and therefore process_event is never called
        # we implemented that function to still update the state if needed even if there is no new sensor value
        # it is useful for the exit condition of the reactive_control
        while True:
            self.updateWithoutSensors()
            await sleep(SLEEP_DURATION)

    def updateWithoutSensors(self):
        dt = time() - self.last_time

        if (
            dt > 7
            and self.ctx.state.reactive_control == True
            and self.computedOnce == False
        ):  # compute the new djikstra with the new position of the thymio
            self.ctx.scene_update.trigger()  # update djisktra
            self.computedOnce = True

        if (
            dt > 8 and self.ctx.state.reactive_control
        ):  # 8 sec passed since the trigger => exit condition of reactive control
            self.computedOnce = False
            self.ctx.state.reactive_control = False
            self.motion_control.setNewWaypoint(1)

    def should_freestyle(self):
        distances = np.array(self.ctx.state.relative_distances)
        distances = distances[:-2]  # remove the 2 back sensors
        distances = distances[distances != -1]
        if len(distances) > 0 and self.ctx.state.reactive_control == False:
            if (
                distances.min() < 3.5
            ):  # if the obstacle is very close => entry condition
                self.ctx.state.reactive_control = True
                self.computedOnce = False
                self.last_time = time()
                return

    def update(self):  # update state variable
        allDistances = self.getDistanceArray()
        self.ctx.state.relative_distances = allDistances.tolist()

    def updateMap(
        self,
    ):  # Updates the map with all new sensed obstacles
        relativeWalls = self.getWallRelative()
        for i in range(len(relativeWalls)):
            if relativeWalls[i] != None:
                globalPos = self.wayPointPerceivedToReal(relativeWalls[i])
                indexes = globalPos / PIXELS_PER_CM
                try:
                    if self.ctx.state.obstacles is not None:
                        self.ctx.state.obstacles[int(indexes[0])][int(indexes[1])] = 1
                except:
                    print("detected wall outside of scope")

    def rotate(self, angle, coords):
        R = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])

        return R.dot(coords.transpose()).transpose()

    def wayPointPerceivedToReal(
        self, wayPointPerceived
    ):  # transforms the perceived waypoint to the real world coordinates
        coords = np.array([wayPointPerceived[0], wayPointPerceived[1]])
        wayPoint = self.rotate(self.ctx.state.orientation, coords)
        [x, y] = wayPoint + np.array([0, 0])
        return np.array([x, y])

    def getDistance(
        self, sensorValue, SensorsValuesConversion
    ):  # convert sensors values [0;4500] to real world cm
        # it takes as arguments the sensor value, and the ref array for the conversion (line 20)
        idx1 = np.abs(SensorsValuesConversion[:, 1] - sensorValue).argmin()
        distance = SensorsValuesConversion[idx1, 1] - sensorValue
        idx2 = idx1 + np.sign(distance)
        # out of range <0 or > 4935
        if idx2 >= len(SensorsValuesConversion[:, 1]):
            return -1
        if idx2 == -1:
            return SensorsValuesConversion[idx1, 0]
        if distance == 0:
            computedDist = SensorsValuesConversion[idx1, 0]
        else:  # if between the ref values => linearly compute the value between both of them
            absoluteDiff = np.abs(
                SensorsValuesConversion[idx2, 1] - SensorsValuesConversion[idx1, 1]
            )
            percentage = distance / absoluteDiff
            computedDist = percentage + SensorsValuesConversion[idx1, 0]
        if computedDist >= 12:
            return -1
        return computedDist

    def getDistanceArray(
        self,
    ):  # array of conversion of all Thymios sensors to real world cm depending on their reference
        proxSensor = np.array(self.ctx.state.prox_sensors)
        proxDistance = []
        proxDistance = proxDistance + [
            self.getDistance(proxSensor[0], SensorsValuesFront)
        ]
        proxDistance = proxDistance + [
            self.getDistance(proxSensor[1], SensorsValuesDiag)
        ]
        proxDistance = proxDistance + [
            self.getDistance(proxSensor[2], SensorsValuesFront)
        ]
        proxDistance = proxDistance + [
            self.getDistance(proxSensor[3], SensorsValuesDiag)
        ]
        proxDistance = proxDistance + [
            self.getDistance(proxSensor[4], SensorsValuesFront)
        ]
        proxDistance = proxDistance + [
            self.getDistance(proxSensor[5], SensorsValuesBack)
        ]
        proxDistance = proxDistance + [
            self.getDistance(proxSensor[6], SensorsValuesBack)
        ]
        return np.array(proxDistance)

    def getWallRelative(
        self,
    ):  # Returns the relative wall position
        distAray = np.array(self.ctx.state.relative_distances)
        obstacle_positions = []
        for i in range(len(distAray)):
            obstacle_positionsi = None
            if distAray[i] != -1:
                obstacle_positionsi = [[], []]
                ti = math.atan2(
                    sensor_pos_from_center[i][1], sensor_pos_from_center[i][0]
                )
                obstacle_positionsi = [
                    sensor_pos_from_center[i][0] + distAray[i] * math.cos(ti),
                    sensor_pos_from_center[i][1] + distAray[i] * math.sin(ti),
                ]
            obstacle_positions = obstacle_positions + [obstacle_positionsi]
        return obstacle_positions
