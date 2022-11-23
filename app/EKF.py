import numpy as np
from app.state import state, State

""" THIS IS A NEW VERSION OF THE FILTER KALMAN.PY AND FILTERING:PY ARE OBSELETE """

class ExtendedKalmanFilter(object):
    """ 
    class containing every necessary function for EKF
    
    @variables:
    Var dt: Time interval between every filtering
    Var E: state vector (px[cm] py[cm] orientation[rad])
    Var A: state transition matrix
    Var B: control transition matrix
    Var U: control vector (forward_speed[cm/s] rotation_speed[rad/s])
    Var G: Jacobian matrix
    Var H: Observation matrix
    Var Q: Noise covariance matrix
    Var R: Measure covariance matrix
    Var P: estimation matrix

    @functions:
    Func __init__: initiates the EKF
    Func predict: from motor reading and past estimation, predict next state
    Func update: from camera vision, update the prediction matrices

    @internal functions:
    Func update_B: updates B matrix from orientation
    Func update_U: updates U matrix from orientation and speed
    Func update_G: updates jacobian from orientation and speed
    """
    def __init__(self, pose, orientation):
        """ 
        initiates the class

        param pose: x,y position in cm
        param orientation: orientation from x axis in rad
        """
        self.dt=0.1 # refresh rate Ts 0.1s

        # State Vector
        self.E=np.matrix([[pose[0]], [pose[1]], [orientation]]) # x, y, orientation

        # transition matrix
        self.A=np.matrix([[1, 0, 0],
                          [0, 1, 0],
                          [0, 0, 1]])

        self.update_B()

        self.update_U(0, 0)

        self.update_G()

        # Matrice d'observation, on observe que x et y
        self.H=np.matrix([[1, 0, 0],
                          [0, 1, 0]])

        self.Q=np.matrix([[1, 0, 0],
                          [0, 1, 0],
                          [0, 0, 1]]) # valeurs uniquement sur la diag, les bruits sont indépendants 

        self.R=np.matrix([[1, 0],
                          [0, 1]]) # bruit de la caméra, peut-être donné par le constructeur.  sinon tuner

        self.P=np.eye(self.A.shape[1])

    def update_B(self):
        """ 
        Updates B matrix
        """
        self.B = np.matrix([[np.cos(self.E[2])*self.dt, 0],
                           [np.sin(self.E[2])*self.dt, 0],
                           [0, self.dt]])
                           
    def update_U(self, speedL, speedR):
        """ 
        Updates U matrix

        param speedL: left wheel speed sensor in cm/s
        param speedR: right wheel speed sensor in cm/s
        """
        speed_forward = (speedL+speedR)/2
        speed_rotation = (speedL-speed_R)/2/30/5   
        self.U = np.matrix([speed_forward], [speed_rotation])

    def update_G(self):
        """ 
        Updates G matrix
        """
        self.G = np.matrix([[1, 0, -np.sin(self.E[2])*self.dt*self.U[0]],
                            [0, 1, np.cos(self.E[2])*self.dt*self.U[0]],
                            [0, 0, 1]])

    def predict(self, speedL, speedR, orientation):
        """ 
        estimates the next state

        param speedL: left wheel speed sensor in cm/s
        param speedR: right wheel speed sensor in cm/s
        param orientation: orientation from x axis in rad

        return E: estimated state
        """
        #MUST UPDATE ORIENTATION BY OFFSET WITH THE MOTORS------------------------------------------------------------------------------------------

        #updates the matrices B,U,G
        self.update_B()
        self.update_U(speedL, speedR)
        self.update_G()

        #computes estimation
        self.E=np.dot(self.A, self.E) + np.dot(self.B,self.U)
        # Calcul de la covariance de l'erreur
        self.P=np.dot(np.dot(self.G, self.P),self.G.T)+self.Q
        return self.E

    def update(self, z):
        """ 
        updates the estimation matrices when camera data is given

        param z: x,y position in cm

        return E: estimated state
        """        
        #WHERE DOES ORIENTATION APPEARS---------------------------------------------------------------------------------------------------------------
        # Calcul du gain de Kalman
        S=np.dot(self.H, np.dot(self.P, self.H.T))+self.R
        K=np.dot(np.dot(self.P, self.H.T), np.linalg.inv(S))

        # Correction / innovation
        self.E=np.round(self.E+np.dot(K, (z-np.dot(self.H, self.E))))
        I=np.eye(self.H.shape[1])
        self.P=(I-(K*self.H))*self.P

        return self.E