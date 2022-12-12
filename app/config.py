# == General == #
DEBUG = False
LOG_LEVEL = 6
RAISE_DEPRECATION_WARNINGS = False
POOL_SIZE = 4
SUBDIVISIONS = 64


# tdmclient
PROCESS_MSG_INTERVAL = 0.1  # time interval between checks if incoming messages

PHYSICAL_SIZE_CM = 110  # physical size of the scene board in cm
THYMIO_TO_CM = 4 / 100  # factor to put the thymio speed in centimetres per seconds
DIAMETER = 9.5  # wheel to wheel distance

# == Big Brain == #
UPDATE_FREQUENCY = 0.2  # frequency of big brain internal loop refresh

# == Vision == #
USE_EXTERNAL_CAMERA = True  # use external camera or webcam
USE_LIVE_CAMERA = True  # use camera or only fix image

SCENE_THRESHOLD = 10  # number of obstacles changes to trigger a scene update
PIXELS_PER_CM = 5  # number of pixels in each cm
TABLE_LEN = 58  # size in cm of the table
LM_FRONT = 2.7  # diameter of the front landmark in cm
LM_BACK = 2.3  # diameter of the back landmark in cm
SAFE_DISTANCE = 15  # distance from the hole of the robot until the further point in cm

# == Second Thymio == #
DROP_SPEED = 50  # speed of the motors to drop the bauble
DROP_TIME = 1.5  # drop duration in seconds
HALF_TURN_SPEED = 50  # speed of the half turn
HALF_TURN_TIME = 8  # time for the thymio to do a 180° turn
