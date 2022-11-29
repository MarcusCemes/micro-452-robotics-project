import cv2
import matplotlib.pyplot as plt
import time
import numpy as np
from scipy import signal
from math import pi

from app.config import PIXELS_PER_CM, TABLE_LEN, LM_FRONT, LM_BACK, SAFE_DISTANCE, FINAL_SIZE
from app.context import Context


class Vision:

    def __init__(self, ctx: Context, external=True, live=True):
        self.ctx = ctx

        # Create a VideoCapture object and read from input file
        # If the input is the camera, pass 0 instead of the video file name
        source = 1 if external else 0
        self.cap = cv2.VideoCapture(source)

        # Check if camera opened successfully
        if (self.cap.isOpened() == False and live == True):
            print("Error opening video stream or file")
            exit(-1)

        # create the masks in BGR
        self.color_obstacles = [(0, 0, 0), (70, 70, 70)]       # black
        self.color_back = [(150, 140, 200), (200, 160, 255)]   # pink
        self.color_front = [(100, 0, 0), (255, 60, 50)]        # blue

        self.table_len = PIXELS_PER_CM*TABLE_LEN

        # live video
        self.live = live

        self.__get_frame()    # init frame
        self.__create_border_filter()   # init border detection filter

    def __get_frame(self, saved_frame='frame.jpeg'):
        if self.live == True:
            ret, self.frame = self.cap.read()
            if ret == False:
                exit(-1)
        else:
            self.frame = cv2.imread(saved_frame)

    def calibrate(self):
        self.n_points = 0
        self.pts_src = np.zeros((4, 2), np.int32)

        pts_dst = np.array([[0, 0], [self.table_len-1, 0],
                           [self.table_len-1, self.table_len-1], [0, self.table_len-1]])

        self.__get_frame()

        while (1):
            cv2.imshow('Frame', self.frame)
            key = cv2.waitKey(5)
            if key == ord('s'):
                break
            if key == ord('n'):
                self.__get_frame()

        cv2.imshow("frame", self.frame)
        cv2.setMouseCallback("frame", self.__mouse_callback)
        while self.n_points < 4:
            cv2.waitKey(10)
        cv2.destroyWindow('frame')

        # Calculate Homography
        self.h, _ = cv2.findHomography(self.pts_src, pts_dst)

    def __mouse_callback(self, event, x, y, flags, params):
        if event == cv2.EVENT_LBUTTONDOWN and self.n_points < 4:  # Left button click
            self.pts_src[self.n_points] = x, y
            self.n_points += 1
        elif event == cv2.EVENT_RBUTTONDOWN:  # Right button click
            print(
                f"coords {x, y}, colors Blue- {self.frame[y, x, 0]} , Green- {self.frame[y, x, 1]}, Red- {self.frame[y, x, 2]} ")

    def update(self):
        self.__get_frame()
        self.__focus_table()
        self.__final_table()
        self.__robot_coordinates()
        return self.table64, (self.final_x, self.final_y, self.theta), (self.robot_x, self.robot_y, self.theta)

    def __focus_table(self):
        self.table = cv2.warpPerspective(
            self.frame, self.h, (self.table_len, self.table_len))
        self.table = cv2.bilateralFilter(self.table, PIXELS_PER_CM, 75, 75)
        self.__erase_noisy_edges()

    def __erase_noisy_edges(self):
        self.obstacles = cv2.inRange(
            self.table, self.color_obstacles[0], self.color_obstacles[1])
        self.obstacles[0:int(PIXELS_PER_CM), :] = 0     # upper margin
        self.obstacles[:, 0:int(PIXELS_PER_CM)] = 0     # left margin
        self.obstacles[-int(PIXELS_PER_CM):, :] = 0     # lower margin
        self.obstacles[:, -int(PIXELS_PER_CM):] = 0     # right margin

    def __create_border_filter(self):
        # add borders to obstacles
        radius = int(SAFE_DISTANCE*PIXELS_PER_CM/(2**(1/2)))
        self.borders = np.zeros((2*radius+1, 2*radius+1))
        for x in range(self.borders.shape[0]):
            for y in range(self.borders.shape[1]):
                if ((x-radius)**2+(y-radius)**2)**(1/2) <= radius:
                    self.borders[x, y] = 1

    def __final_table(self):
        self.__add_borders()
        # send this information o the next module
        self.table64 = cv2.flip(cv2.resize(self.obstacles, dsize=(
            FINAL_SIZE, FINAL_SIZE)), 0)  # changing the referencial on yy

    def __add_borders(self):
        # add borders
        self.obstacles_borders = signal.convolve2d(
            self.obstacles, self.borders, mode='same', boundary='fill', fillvalue=0)
        self.obstacles = (255*(self.obstacles_borders > 0)).astype(np.uint8)

    def __robot_coordinates(self):
        self.__detect_robot_marks()
        self.__get_angle()
        self.robot_x, self.robot_y, self.theta = self.center_back[0], TABLE_LEN * \
            PIXELS_PER_CM - self.center_back[1], -self.theta
        self.final_x, self.final_y = int(self.robot_x*FINAL_SIZE/(
            TABLE_LEN*PIXELS_PER_CM)), int(self.robot_y*FINAL_SIZE/(TABLE_LEN*PIXELS_PER_CM))

    def __detect_robot_marks(self):
        # front of the robot
        robot_front = cv2.inRange(
            self.table, self.color_front[0], self.color_front[1])
        filter_front = np.ones(
            (int(LM_FRONT*PIXELS_PER_CM), int(LM_FRONT*PIXELS_PER_CM)))
        self.center_front = signal.convolve2d(
            robot_front, filter_front, mode='same', boundary='fill', fillvalue=0)
        self.center_front = (np.argmax(self.center_front) % self.center_front.shape[1], np.argmax(
            self.center_front)//self.center_front.shape[1])  # (x,y)

        # back of the robot
        robot_back = cv2.inRange(
            self.table, self.color_back[0], self.color_back[1])
        filter_back = np.ones(
            (int(LM_BACK*PIXELS_PER_CM), int(LM_BACK*PIXELS_PER_CM)))
        self.center_back = signal.convolve2d(
            robot_back, filter_back, mode='same', boundary='fill', fillvalue=0)
        self.center_back = (np.argmax(self.center_back) % self.center_back.shape[1], np.argmax(
            self.center_back)//self.center_back.shape[1])

    def __get_angle(self):
        # get the coordinates of the robot
        self.theta = np.arctan((self.center_front[1]-self.center_back[1])/(self.center_front[0]-self.center_back[0]))*180 / \
            pi if self.center_front[0] != self.center_back[0] else 90 if self.center_front[1] > self.center_back[1] else -90

        # 3rd and 4th quadrant
        if self.center_front[0] < self.center_back[0]:
            if self.theta < 0:
                self.theta += 180              # 4th quadrant
            else:
                self.theta -= 180              # 3rd quadrant

    def view(self):
        cv2.circle(self.obstacles, self.center_front, int(
            LM_FRONT*PIXELS_PER_CM/2), (255, 255, 255), 2)
        cv2.circle(self.obstacles, self.center_back, int(
            LM_BACK*PIXELS_PER_CM/2), (255, 255, 255), 2)
        dist = 1.8*((self.center_front[0]-self.center_back[0]) **
                    2+(self.center_front[1]-self.center_back[1])**2)**(1/2)
        table290 = cv2.arrowedLine(cv2.flip(self.obstacles, 0), (self.robot_x, self.robot_y), (int(
            self.robot_x+dist*np.cos(self.theta*pi/180)), int(self.robot_y+dist*np.sin(self.theta*pi/180))), (255, 255, 255), 2, tipLength=0.5)
        cv2.imshow("live view", cv2.flip(table290, 0))

    def __del__(self):
        self.cap.release()
        cv2.destroyAllWindows()


'''
if __name__ == "__main__":
    Camera = Vision()
    Camera.calibrate()  # calibrate the image so it focuses on the table

    key = 0
    while (1):
        key = cv2.waitKey(1)
        if key == ord('q'):
            break

        occupancy_64, coordinates_64, coordinates_cm = Camera.update()
        Camera.view()

'''
'''
from dataclasses import dataclass
from time import time
from typing import Any

import numpy as np

from app.context import Context


@dataclass
class Frame:
    position: tuple[float, float]
    orientation: float
    obstacles: Any


class Vision():

    def __init__(self, ctx: Context):
        self.ctx = ctx
        self.last_update = time()

    def next_frame(self, subdivisions: int):
        image = self.capture_image()
        return self.process_image(image, subdivisions)

    def capture_image(self):
        # capture image
        pass

    def process_image(self, image, subdivisions) -> Frame:
        # process image
        obstacles = np.array([subdivisions, subdivisions], dtype=np.int8)
        return Frame((0, 0), 0, obstacles)
'''
