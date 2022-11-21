from app.state import state, update_state
from app.kalman import kalman_filter_1D


# idea: have a thymio_data_speed array to store the speed of the motors since the beggining
thymio_data_speed = []
states_data = []
Ts = 0.1 # scan period


""" def motors(left, right):
    return {
        "motor.left.target": [left],
        "motor.right.target": [right],
    }

def get_data():
    thymio_data_speed.append({"left_speed":node["motor.left.speed"],
                        "right_speed":node["motor.right.speed"]})
     """

def get_speed_x_y(orientation, speed_left, speed_right):
    """ decomposes the speed in the axis base
    
        param orientation: orientation of the thymio in [rad] (0 is facing north)
        param speed_left: speed given by the left motor in thymio units
        param speed_right: speed given by the right motor in thymio units
        
        return speed_left_x: left speed along the x axis
        return speed_left_y: left speed along the y axis
        return speed_right_x: right speed along the x axis
        return speed_right_y: right speed along the y axis
    """
    sinor = math.sin(orientation)
    cosor = math.cos(orientation)

    speed_left_x = sinor*speed_left
    speed_right_x = sinor*speed_right

    speed_left_y = cosor*speed_left
    speed_right_y = cosor*speed_right

    return speed_left_x, speed_left_y, speed_right_x, speed_right_y



def filtering(current_state, speed_left, speed_right):

    """    Runs the filtering pipeline once, must be called each time a state is measured
        
        param state: current state the thymio is in from vision
            containing: x position [cm], y position [cm], orientation [rad]
        param speed_left: speed given by the left motor in thymio units
        param speed_right: speed given by the right motor in thymio units
        
        return state_est: estimmation of the state
    """   

    # add something to fill the thymio_data_speed array

    states_data.append = current_state # data containing states since the beggining
    thymio_data_speed.append({"left_speed":node["motor.left.speed"],
                            "right_speed":node["motor.right.speed"]})

    l_speed = [x["left_speed"] for x in thymio_data_speed]
    r_speed = [x["right_speed"] for x in thymio_data_speed]

    avg_speed = [(x["left_speed"]+x["right_speed"])/2 for x in thymio_data_speed] # MAYBE DIFFERENTIATE DIRECTIONS OF VELOCITY

    thymio_speed_to_mms = 2.5 # 500 thymio speed = 200 mm/s

    var_speed = np.var(avg_speed[:]/thymio_speed_to_mms)
    std_speed = np.std(avg_speed[:]/thymio_speed_to_mms)

    q_nu = std_speed/2 # variance on speed state
    r_nu = std_speed/2 # variance on speed measurement 

    qp = 0.04 # variance on position state
    rp = 0.25 # variance on position measurement 

    x_est = [np.array([[0], [0]])] # POSITION, VELOCITY in x direction
    Px_est = [1000 * np.ones(2)]
    cam_pos_x = [avg_cam_pos_x[k0-1]]
    speed_x = [avg_speed_x[k0-1]]

    y_est = [np.array([[0], [0]])] # POSITION, VELOCITY in y direction
    Py_est = [1000 * np.ones(2)]
    cam_pos_y = [avg_cam_pos_y[k0-1]]
    speed_y = [avg_speed_y[k0-1]]

    k0 = 0 #initial offset (not sure if usefull for the project)

    for k in tqdm(range(k0, len(states_data))):
        speed_x.append(avg_speed_x[k])
        cam_pos_x.append(avg_cam_pos_x[k])

        speed_y.append(avg_speed_y[k])
        cam_pos_y.append(avg_cam_pos_y[k])

        new_x_est, new_Px_est = kalman_filter(speed_x[-1], cam_pos_x[-2], cam_pos_x[-1], x_est[-1], P_est[-1])
        x_est.append(new_x_est) # x estimmation
        Px_est.append(new_Px_est)

        new_y_est, new_Py_est = kalman_filter(speed_y[-1], cam_pos_y[-2], cam_pos_y[-1], x_est[-1], P_est[-1])
        y_est.append(new_y_est) # y estimmation
        Py_est.append(new_Py_est)
        
    return new_x_est, new_y_est