from math import pi

import cv2
import numpy as np
from scipy.signal import convolve2d
import matplotlib as plt

from app.config import *
from app.context import Context
from app.utils.console import *

THRESHOLD = 128

CALIBRATE_NAMED_WINDOW = "Calibrate camera perspective"

COLORS = (
    (35, 35, 35), #BLACK
    (170, 150, 225), #PINK
    (60, 125, 50), #GREEN
    (210, 210, 210), #WHITE
)

CAPTURE_SOURCE = None

def close_capture_source():
    if CAPTURE_SOURCE is not None:
        CAPTURE_SOURCE.release()

class Vision:

    def __init__(self, ctx: Context, external=True, live=False):
        global CAPTURE_SOURCE

        self.ctx = ctx

        # Create a VideoCapture object and read from input file
        # If the input is the camera, pass 0 instead of the video file name
        source = 1 if external else 0
        self.cap = cv2.VideoCapture(source, cv2.CAP_DSHOW)
        CAPTURE_SOURCE = self.cap

        # Check if camera opened successfully
        if (self.cap.isOpened() == False and live == True):
            print("Error opening video stream or file")
            exit(-1)

        # create the masks in BGR
        self.color_obstacles = [(0, 0, 0), (70, 70, 70)]       # black
        self.color_back = [(150, 100, 200), (210, 160, 255)]   # pink
        self.color_front = [(30, 100, 30), (80, 150, 70)]        # blue
        

        self.table_len = PIXELS_PER_CM*TABLE_LEN

        # live video
        self.live = live

        self.__get_frame()    # init frame
        self.__create_border_filter()   # init border detection filter

    def __get_frame(self, saved_frame='assets/test_frame_01.jpg'):
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

        if not self.live:
            self.pts_src = np.array(
                [[80, 9], [525, 14], [518, 464], [76, 460]])
        else:
            self.__get_frame()

            info("Select 4 points to correct perspective (TL, TR, BR, BL)")
            info("Press N to take a new frame, or Q to exit")

            cv2.imshow(CALIBRATE_NAMED_WINDOW, self.frame)
            cv2.setMouseCallback(CALIBRATE_NAMED_WINDOW, self.__mouse_callback)

            while self.n_points < 4:
                key = cv2.waitKey(1)

                if key == ord("q"):
                    exit(0)

                elif key == ord("n"):
                    self.pts_src = np.zeros((4, 2), np.int32)
                    self.n_points = 0

                    self.__get_frame()
                    cv2.imshow(CALIBRATE_NAMED_WINDOW, self.frame)

            cv2.destroyWindow(CALIBRATE_NAMED_WINDOW)

        # Calculate Homography
        debug("Selected points:", self.pts_src)
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
        
        self.table = self.get_Image_Color_array()
        self.__robot_coordinates()

        # degrees to radiants
        theta_rad = self.theta * pi/180
        #theta_rad = 0

        return self.table64, (self.final_x, self.final_y, theta_rad), ((self.final_x/FINAL_SIZE)*TABLE_LEN, (self.final_y/FINAL_SIZE)*TABLE_LEN, theta_rad), (self.front_mark_x, self.front_mark_y), ((self.front_mark_x/FINAL_SIZE)*TABLE_LEN, (self.front_mark_y/FINAL_SIZE)*TABLE_LEN)

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
        # self.__add_borders()
        # send this information o the next module
        self.table64 = cv2.flip(cv2.resize(self.obstacles, dsize=(
            FINAL_SIZE, FINAL_SIZE)), 0)  # changing the referencial on yy

        # Clip values using a threshold value
        self.table64 = np.where(self.table64 > THRESHOLD, 1, 0)

    def __add_borders(self):
        # add borders
        self.obstacles_borders = convolve2d(
            self.obstacles, self.borders, mode='same', boundary='fill', fillvalue=0)
        self.obstacles = (255*(self.obstacles_borders > 0)).astype(np.uint8)

    def __robot_coordinates(self):
        self.__detect_robot_marks()
        self.__get_angle()
        self.robot_x, self.robot_y, self.theta = self.center_back[0], TABLE_LEN * \
            PIXELS_PER_CM - self.center_back[1], -self.theta
        self.final_x, self.final_y = int(self.robot_x*FINAL_SIZE/(
            TABLE_LEN*PIXELS_PER_CM)), int(self.robot_y*FINAL_SIZE/(TABLE_LEN*PIXELS_PER_CM))
        self.front_mark_x, self.front_mark_y = self.center_front[0], TABLE_LEN * \
            PIXELS_PER_CM - self.center_front[1]
        self.front_mark_x, self.front_mark_y = int(self.front_mark_x*FINAL_SIZE/(
            TABLE_LEN*PIXELS_PER_CM)), int(self.front_mark_y*FINAL_SIZE/(TABLE_LEN*PIXELS_PER_CM))

    def __detect_robot_marks(self):
        # front of the robot
        robot_front = cv2.inRange(
            self.table, self.color_front[0], self.color_front[1])
        filter_front = np.ones(
            (int(LM_FRONT*PIXELS_PER_CM), int(LM_FRONT*PIXELS_PER_CM)))
        self.center_front = convolve2d(
            robot_front, filter_front, mode='same', boundary='fill', fillvalue=0)
        self.center_front = (np.argmax(self.center_front) % self.center_front.shape[1], np.argmax(
            self.center_front)//self.center_front.shape[1])  # (x,y)

        # back of the robot
        robot_back = cv2.inRange(
            self.table, self.color_back[0], self.color_back[1])
        filter_back = np.ones(
            (int(LM_BACK*PIXELS_PER_CM), int(LM_BACK*PIXELS_PER_CM)))
        self.center_back = convolve2d(
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

    def closest_color(self, px):
        r, g, b = px
        color_diffs = []
        for color in COLORS:
            cr, cg, cb = color
            color_diff = np.sqrt((r - cr)**2 + (g - cg)**2 + (b - cb)**2)
            color_diffs.append((color_diff, color))
        return min(color_diffs)[1]

    def get_Image_Color_array(self):
        if(self.table is None):
            return
        try:
            color_array = (self.table)
            for i in range(len(color_array)):
                for j in range(len(color_array[i])):
                    color_array[i][j] = self.closest_color(color_array[i][j])
            return color_array
        except:
            print("error shwon")


    def visualise_dots(self):
        # front of the robot
        robot_front = cv2.inRange(
            self.table, self.color_front[0], self.color_front[1])
        plt.imshow(robot_front)

        # filter_front = np.ones(
        #     (int(LM_FRONT*PIXELS_PER_CM), int(LM_FRONT*PIXELS_PER_CM)))
        # center_front = convolve2d(
        #     robot_front, filter_front, mode='same', boundary='fill', fillvalue=0)
        # self.center_front = (np.argmax(self.center_front) % self.center_front.shape[1], np.argmax(
        #     self.center_front)//self.center_front.shape[1])  # (x,y)

        # back of the robot
        # robot_back = cv2.inRange(
        #     self.table, self.color_back[0], self.color_back[1])
        # filter_back = np.ones(
        #     (int(LM_BACK*PIXELS_PER_CM), int(LM_BACK*PIXELS_PER_CM)))
        # self.center_back = convolve2d(
        #     robot_back, filter_back, mode='same', boundary='fill', fillvalue=0)
        # self.center_back = (np.argmax(self.center_back) % self.center_back.shape[1], np.argmax(
        #     self.center_back)//self.center_back.shape[1])

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
