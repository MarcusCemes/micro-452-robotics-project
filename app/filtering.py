from tdmclient import ClientAsync, aw
import math
import numpy as np

from app.state import state
from app.EKF import ExtendedKalmanFilter

THYMIO_TO_CM = 3.85/100 #NEEDS TO BE MODIFIED ACCORDING TO THE THYMIO

#doing only once as a declaration (maybe to move elswere)
ekf = ExtendedKalmanFilter(0, 0, math.pi()/2)

def filtering(current_state):# current state is a class

    """    Runs the filtering pipeline once, must be called each time a state is measured
        
        param current_state: current state the thymio is in from vision
            containing: x position [cm], y position [cm], orientation [rad] 
        
        return state: estimmation of the state (is there realy an use for that?)
    """   
    
    speedL = node["motor.left.speed"] #in thymio units
    speedR = node["motor.right.speed"] #in thymio units

    #speed transformation from thymio units to cm/s
    speedL = speedL * THYMIO_TO_CM
    speedR = speedR * THYMIO_TO_CM

    #blind estimation of the next state
    state.position[0], state.position[1], state.orientation = ekf.predict(speedL, speedR)

    #if camera reading, estimation of the next state with measurement
    pose = np.matrix([current_state.position[0], current_state.position[1], current_state.orientation])

    if(pose[0] != 0 and pose[1] != 0): #verify condition (not sure)---------------------------------------------------------------------------------------------------------------
        KF.update(pose)

    #send global state
    state.mark_stale()

    return state