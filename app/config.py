# == General == #
DEBUG = False
LOG_LEVEL = 6
RAISE_DEPRECATION_WARNINGS = False
POOL_SIZE = 4
SUBDIVISIONS = 64


# tdmclient
PROCESS_MSG_INTERVAL = 0.1

PHYSICAL_SIZE_CM = 120
SLEEP_INTERVAL = 0.1
THYMIO_TO_CM = 3.85/100  # NEEDS TO BE MODIFIED ACCORDING TO THE THYMIO
DIAMETER = 9.5
DT_THRESHOLD = 0.6

# == Vision == #
USE_EXTERNAL_CAMERA = False
USE_LIVE_CAMERA = False

SCENE_THRESHOLD = 2  # number of obstacles changes to trigger a scene update
PIXELS_PER_CM = 5   # number of pixels in each cm
TABLE_LEN = 58      # size in cm of the table
LM_FRONT = 2.7      # diameter of the front landmark in cm
LM_BACK = 3.2      # diameter of the back landmark in cm
SAFE_DISTANCE = 10   # distance from the hole of the robot until the further point in cm
FINAL_SIZE = 64     # size of the final matrix sent to the path planning module

# == Second Thymio == #
DROP_SPEED = 50     # speed of the motors to drop the baulbe
DROP_TIME = 1.5       # drop duration in seconds
