from app.state import state, update_state
from app.kalman import kalman_filter_1D

""" OBSELETE """

# idea: have a thymio_data_speed array to store the speed of the motors since the beggining
thymio_data_speed = []
states_data = [] # containing states (x pos, y pos, orientation)
Ts = 0.1 # scan period

last_cam_state = State(
    position=(0.5, 1.4),
    orientation=(math.pi/2),
    start=(0.4, 0.4),
    end=(1.6, 1.6),
    physical_size=(BOARD_SIZE_M, BOARD_SIZE_M),
    path=[],
    obstacles=[],
    computation_time=0.0
) #INITIAL STATE FOR DECLARATION

x_est = 0 # initial x position
Px_est = [10 * np.ones(2)] #estimation de a quel point la caméra a raison

y_est = 0 # initial y position
Py_est = [10 * np.ones(2)]

# to compute beforehand
q_nu = std_speed/2 # variance on speed state
r_nu = std_speed/2 # variance on speed measurement 

qp = 0.04 # variance on position state
rp = 0.25 # variance on position measurement 


def get_speed_x_y(orientation, speed_left, speed_right):
    """ decomposes the speed in the axis base
    
        param orientation: orientation of the thymio in [rad] (0 is facing east)
        param speed_left: speed given by the left motor in thymio units
        param speed_right: speed given by the right motor in thymio units
        
        return speed_x: forward speed along the x axis
        return speed_y: forward speed along the y axis
    """
    sinor = math.sin(orientation)
    cosor = math.cos(orientation)

    forward_speed = (speed_left + speed_right) / 2

    speed_x = cosor * forward_speed

    speed_y = sinor * forward_speed

    return speed_x, speed_y


def filtering(current_state, speed_left, speed_right):

    """    Runs the filtering pipeline once, must be called each time a state is measured
        
        param current_state: current state the thymio is in from vision
            containing: x position [cm], y position [cm], orientation [rad]
        param speed_left: speed given by the left motor in cm/s units
        param speed_right: speed given by the right motor in cm/s thymio units
        
        return state_est: estimmation of the state
    """   

    # update orientation
    rotation_speed = (speed_left - speed_right) /2 /30 /5
    diffOr = rotation_speed * Ts
    orientation_new = orientation + diffOr
    if (orientation_new > 2*math.pi):
        orientation_new = orientation_new - 2*math.pi

    # local variables
    speed_x, speed_y = get_speed_x_y(orientation_new, speed_left, speed_right)

    (cam_previous_pos_x, cam_previous_pos_y) = last_cam_state.position
    (cam_pos_x, cam_pos_y) = current_state.position

    # Filtering
    new_x_est, new_Px_est = kalman_filter_1D(speed_x, cam_previous_pos_x, cam_pos_x, x_est, Px_est, orientation_new)
    x_est = new_x_est # x estimmation
    Px_est = new_Px_est

    new_y_est, new_Py_est = kalman_filter_1D(speed_y, cam_previous_pos_y, cam_pos_y, y_est, Py_est, orientation_new)
    y_est = new_y_est # y estimmation
    Py_est = new_Py_est

    last_cam_state.update_state_position(current_state.position) #TO IMPLEMENT IN STATE
    
    #create output state
    state_est = State()
    state_est.position = (x_est, y_est)
    state_est.orientation = orientation_new

    #update global state
    state.position = (x_est, y_est)
    state.orientation = orientation_new
    state.mark_stale()

    return state_est