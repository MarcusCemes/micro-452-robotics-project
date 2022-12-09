
def stop_movement_simulation(filtering):
    filtering.process_event({"motor.left.speed": [0], "motor.right.speed": [0]})

def print_pose(ctx):
    print(f"position of the thymio: {ctx.state.position}")
    print(f"orientation: {ctx.state.orientation}")
    return 

