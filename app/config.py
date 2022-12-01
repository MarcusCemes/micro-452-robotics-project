DEBUG = False
RAISE_DEPRECATION_WARNINGS = False
PROCESS_MSG_INTERVAL = 0.1

PHYSICAL_SIZE = (120, 120)
POOL_SIZE = 4
SLEEP_INTERVAL = 0.1
SUBDIVISIONS = 64
THYMIO_TO_CM = 3.85/100  # NEEDS TO BE MODIFIED ACCORDING TO THE THYMIO
DIAMETER = 9.5
DT_THRESHOLD = 0.6

# == Vision == #
PIXELS_PER_CM = 5   # number of pixels in each cm
TABLE_LEN = 58      # size in cm of the table
LM_FRONT = 2.7      # diameter of the front landmark in cm
LM_BACK = 3.2      # diameter of the back landmark in cm
SAFE_DISTANCE = 6   # distance from the hole of the robot until the further point in cm
FINAL_SIZE = 64     # size of the final matrix sent to the path planning module
