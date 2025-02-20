import matplotlib.pyplot as plt
import numpy as np


# REWORK Functions:
def align_center(sensor, hexapod, depth = 0):
    # FUNCION ONLY USED FOR TESTING
    # DONT USE IN THE FINAL VERSION


    # allign beam to center of sensor recursivly
    # assumes the sensor detects the beam
    resolutions = [0.1, 0.01] # also use [0.1, 0.01, 0.001, 0.0001]

    if depth == len(resolutions):
        return True

    step_size = resolutions[depth]

    iterations = 0
    center = 0.5

    aligned = False

    while iterations < 50:
        iterations += 1

        #signal = sensor.get_signal() 
        if sensor.xpos is None or sensor.ypos is None:
            sensor.get_test_signal()


        print(f'Signal x: {sensor.xpos}, y: {sensor.ypos}')
        plt.plot(sensor.xpos, sensor.ypos, 'o')
        print(f'Hex Position: {hexapod.position}')

        if sensor.xpos > center+step_size:
            hexapod.move([-step_size, 0, 0, 0, 0, 0], flag = "relative") # TODO xpos and ypos changes only for testing purposes
            #sensor.xpos -= step_size
            
        elif sensor.xpos < center-step_size:
            hexapod.move([step_size, 0, 0, 0, 0, 0], flag = "relative")
            #sensor.xpos += step_size
        
        elif sensor.ypos > center+step_size:
            hexapod.move([0, 0, -step_size, 0, 0, 0], flag = "relative")
            #sensor.ypos -= step_size
            
        elif sensor.ypos < center-step_size:
            hexapod.move([0, 0, step_size, 0, 0, 0], flag = "relative")
            #sensor.ypos += step_size

        else:
            align_center(sensor, hexapod, depth+1)
            aligned = True
            break

    return aligned

def fine_alignment(sensor, hexapod):
    
    aligned = False
       

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(sensor.xpos, sensor.ypos, 'o')

    ax.set_xlabel('X Position')
    ax.set_ylabel('Y Position')
    ax.set_title('Sensor Output')
    ax.grid(True)
    ax.legend(['Signal Position'])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    aligned = align_center(sensor, hexapod)
        
    plt.show()
    print(f'Aligned: {aligned}')
    print(f'Final Position: {sensor.xpos}, {sensor.ypos}')

    return aligned

def rough_alignment(sensor, hexapod, probe):
    aligned = False
    
    hexapod.move_to_default_position()

    return aligned
