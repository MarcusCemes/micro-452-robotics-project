from app.state import state, update_state

Ts   = 0.1 # scan period

qp   = 0 # variance on position state
q_nu = 0 # variance on speed state

rp   = 0 # variance on position measurement 
r_nu = 0 # variance on speed measurement 

# Initialising the remaining constants
# units: length [mm], time [s]
A = np.array([[1, Ts], [0, 1]])
stripe_width = 50
Q = np.array([[qp, 0], [0, q_nu]]);
speed_conv_factor = 0.3375;

def kalman_filter_1D(speed, cam_prev, cam_state, pos_last_trans, x_est_prev, P_est_prev,
                  HT=None, HNT=None, RT=None, RNT=None):
    """
    Estimates the current state using input sensor data and the previous state
    
    param speed: measured speed (Thymio units)
    param cam_pos_prev: previous pos value measured by camera
    param cam_pos: pos measured by camera
    param x_est_prev: previous state a posteriori estimation
    param P_est_prev: previous state a posteriori covariance
    
    return x_est: new a posteriori state estimation
    return P_est: new a posteriori state covariance
    """
    
    ## Prediciton through the a priori estimate
    # estimated mean of the state
    x_est_a_priori = np.dot(A, x_est_prev);
    
    # Estimated covariance of the state
    P_est_a_priori = np.dot(A, np.dot(P_est_prev, A.T));
    P_est_a_priori = P_est_a_priori + Q if type(Q) != type(None) else P_est_a_priori
    
    ## Update         
    # y, C, and R for a posteriori estimate, depending on transition
    if (cam_pos != 0) : # Is there a measurement of the state from camera (position 0 is no measure)
        # transition detected
        y = np.array([[cam_pos_prev],[speed*speed_conv_factor]])
        H = np.array([[1, 0],[0, 1]])
        R = np.array([[rp, 0],[0, r_nu]])
    else:
        # no transition, use only the speed
        y = speed*speed_conv_factor;
        H = np.array([[0, 1]])
        R = r_nu;

    # innovation / measurement residual
    i = y - np.dot(H, x_est_a_priori);
    # measurement prediction covariance
    S = np.dot(H, np.dot(P_est_a_priori, H.T)) + R;
             
    # Kalman gain (tells how much the predictions should be corrected based on the measurements)
    K = np.dot(P_est_a_priori, np.dot(H.T, np.linalg.inv(S)));
    
    
    # a posteriori estimate
    x_est = x_est_a_priori + np.dot(K,i);
    P_est = P_est_a_priori - np.dot(K,np.dot(H, P_est_a_priori));
     
    return x_est, P_est