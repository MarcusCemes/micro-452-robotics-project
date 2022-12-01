from typing import Any
import numpy as np
import math
from time import time

from app.context import Context
from app.motion_control import MotionControl
from app.utils.background_task import BackgroundTask
from app.utils.event_processor import ThymioEventProcessor
from app.config import PIXELS_PER_CM, FINAL_SIZE


center_offset = np.array([5.5, 5.5])
thymio_coords = np.array([[0, 0], [11, 0], [11, 8.5], [10.2, 9.3],
                          [8, 10.4], [5.5, 11], [3.1, 10.5],
                          [0.9, 9.4], [0, 8.5], [0, 0]])-center_offset

sensor_pos_from_center = np.array([[0.9, 9.4], [3.1, 10.5], [5.5, 11.0], [
                                  8.0, 10.4], [10.2, 9.3], [8.5, 0], [2.5, 0]])-center_offset
SensorsValuesFront = np.array([[1, 4771], [2, 4684], [3, 4542], [4, 4150], [
                              5, 3720], [6, 3383], [7, 3100], [8, 2827], [9, 2600], [10, 2400], [11, 2116]])
SensorsValuesDiag = np.array([[1, 4759], [2, 4702], [3, 4600], [4, 4314], [
                             5, 3909], [6, 3547], [7, 3254], [8, 3008], [9, 2745], [10, 2500], [11, 2250]])
SensorsValuesBack = np.array([[1, 4992], [2, 4929], [3, 4762], [4, 4276], [
                             5, 3744], [6, 3319], [7, 2977], [8, 2716], [9, 2489], [10, 2279], [11, 2072]])
thymiospeed_to_cm = 21.73913043478261/50/10


class LocalNavigation(ThymioEventProcessor):

    def __init__(self, ctx: Context, motion_control: MotionControl):
        self.ctx = ctx
        self.motion_control = motion_control

        self.map = np.array((FINAL_SIZE, FINAL_SIZE), dtype=bool)
        self.last_time = time()

    def should_freestyle(self):
        distances = np.array(self.ctx.state.relative_distances)
        if (distances.min() < 3.5):
            self.ctx.state.reactive_control = True
            self.last_time = time()
            return

        now = time()
        dt = now - self.last_time
        if dt > 1.5 and self.ctx.state.reactive_control:
            self.ctx.state.reactive_control = False
            self.motion_control.setNewWaypoint()

    def update(self):
        allDistances = self.getDistanceArray()
        self.ctx.state.relative_distances = allDistances.tolist()

    def updateMap(self):
        relativeWalls = self.getWallRelative()
        for i in range(len(relativeWalls)):
            if (relativeWalls[i] != None):
                globalPos = self.wayPointPerceivedToReal(relativeWalls[i])
                indexes = globalPos/PIXELS_PER_CM
                self.map[int(indexes[0])][int(indexes[1])] = True

    def process_event(self, variables: dict[str, Any]):
        self.ctx.state.prox_sensors = variables["prox.horizontal"]
        self.ctx.state.changed()

        self.update()
        self.should_freestyle()

    def rotate(self, angle, coords):
        R = np.array([[np.cos(angle), -np.sin(angle)],
                      [np.sin(angle),  np.cos(angle)]])

        return R.dot(coords.transpose()).transpose()

    def wayPointPerceivedToReal(self, wayPointPerceived):
        pos = self.ctx.state.position
        coords = np.array([wayPointPerceived[0], wayPointPerceived[1]])
        wayPoint = self.rotate(self.ctx.state.orientation, coords)
        [x, y] = wayPoint+np.array([0, 0])
        return np.array([x, y])

    def getDistance(self, sensorValue, SensorsValuesConversion):
        idx1 = np.abs(SensorsValuesConversion[:, 1] - sensorValue).argmin()
        distance = SensorsValuesConversion[idx1, 1] - sensorValue
        idx2 = idx1+np.sign(distance)
        # out of range <0 or > 4935
        if (idx2 >= len(SensorsValuesConversion[:, 1])):
            return -1
        if (idx2 == -1):
            return SensorsValuesConversion[idx1, 0]
        if (distance == 0):
            computedDist = SensorsValuesConversion[idx1, 0]
        else:
            absoluteDiff = np.abs(
                SensorsValuesConversion[idx2, 1]-SensorsValuesConversion[idx1, 1])
            percentage = (distance/absoluteDiff)
            computedDist = percentage+SensorsValuesConversion[idx1, 0]
        if (computedDist >= 12):
            return -1
        return computedDist

    def getDistanceArray(self):
        proxSensor = np.array(self.ctx.state.prox_sensors)
        proxDistance = []
        proxDistance = proxDistance + \
            [self.getDistance(proxSensor[0], SensorsValuesFront)]
        proxDistance = proxDistance + \
            [self.getDistance(proxSensor[1], SensorsValuesDiag)]
        proxDistance = proxDistance + \
            [self.getDistance(proxSensor[2], SensorsValuesFront)]
        proxDistance = proxDistance + \
            [self.getDistance(proxSensor[3], SensorsValuesDiag)]
        proxDistance = proxDistance + \
            [self.getDistance(proxSensor[4], SensorsValuesFront)]
        proxDistance = proxDistance + \
            [self.getDistance(proxSensor[5], SensorsValuesBack)]
        proxDistance = proxDistance + \
            [self.getDistance(proxSensor[6], SensorsValuesBack)]
        return np.array(proxDistance)

    def getWallRelative(self):
        distAray = np.array(self.ctx.state.relative_distances)
        obstacle_positions = []
        for i in range(len(distAray)):
            obstacle_positionsi = None
            if (distAray[i] != -1):
                obstacle_positionsi = [[], []]
                ti = math.atan2(
                    sensor_pos_from_center[i][1], sensor_pos_from_center[i][0])
                obstacle_positionsi = [sensor_pos_from_center[i][0] + distAray[i]*math.cos(
                    ti),  sensor_pos_from_center[i][1] + distAray[i]*math.sin(ti)]
            obstacle_positions = obstacle_positions+[obstacle_positionsi]
        return (obstacle_positions)
