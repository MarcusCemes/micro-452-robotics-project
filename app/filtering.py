from app.state import state, update_state

x_est = [np.array([[0], [0]])] # POSITION, VELOCITY in x direction
Px_est = [1000 * np.ones(2)]
cam_pos_x = [avg_cam_pos_x[k0-1]]
speed_x = [avg_speed_x[k0-1]]

y_est = [np.array([[0], [0]])] # POSITION, VELOCITY in y direction
Py_est = [1000 * np.ones(2)]
cam_pos_y = [avg_cam_pos_y[k0-1]]
speed_y = [avg_speed_y[k0-1]]

k0 = 55 #initial offset (not sure if usefull for the project)

states_data = 0 # data containing states since the beggining

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

