import time
from Python_Skripts.Function_Groups.marker_detection import detect_markers
from Python_Skripts.Function_Groups.probe_tip_detection import draw_probe_tip
import cv2
import numpy as np


def update_camera(root):
        while root.camera_object.updating:      
            if root.camera.IsOpen() is True:
                try:
                    root.toggle_camera_var.set(1) # if camera is opened by other means than toggle button
                    image = root.camera_object.capture_image()

                    if root.draw_markers_var.get() == 1:

                        mtx = root.camera_object.mtx
                        dist = root.camera_object.dist
                        sensor_marker_size = root.sensor.marker_size
                        probe_marker_size = root.probe.marker_size 

                        marker_size = sensor_marker_size # for now assume same size TODO implement different sizes
                        
                        # marker drawn in detect markers
                        image, marker_rvecs, marker_tvecs = detect_markers(image, marker_size, mtx, dist)

                        if root.camera_object.camera_calibrated:
                            if len(marker_tvecs) > 0 and len(marker_rvecs) > 0 :
                                root.sensor.marker_rvecs = marker_rvecs[root.sensor.marker_id]
                                root.sensor.marker_tvecs = marker_tvecs[root.sensor.marker_id]
                                root.probe.marker_rvecs = marker_rvecs[root.probe.marker_id]
                                root.probe.marker_tvecs = marker_tvecs[root.probe.marker_id]

                                #print("Sensor Marker tvecs: ", root.sensor.marker_tvecs)
                                #print("Probe Marker tvecs: ", root.probe.marker_tvecs)

                    if root.draw_probe_tip_var.get() == 1:
                        image = draw_probe_tip(image, root.probe.probe_tip_position_in_camera_image)

                    if root.draw_checkerboard_var.get() == 1:
                        image = draw_calibration(root, image)


                    # Update Camera Image
                    canvas = root.camera_plot_frame.canvas
                    ax = canvas.figure.axes[0]
                    
                    ax.clear()
                    ax.imshow(image)
                    
                    #root.log.log_event(f"{ax.get_xlim()} , {ax.get_ylim()}")
                    
                    if (root.camera_object.current_xlim is not None) and (root.camera_object.current_ylim is not None):
                        # set limits to current limits
                        #print("Setting limits to current limits")
                        #print(f"Current limits: {root.camera_object.current_xlim}, {root.camera_object.current_ylim}")
                        ax.set_xlim(root.camera_object.current_xlim)
                        ax.set_ylim(root.camera_object.current_ylim)
                    else:
                        #set initial limits
                        #print("Setting initial limits")
                        root.camera_object.set_current_limits(ax.get_xlim(), ax.get_ylim())
                    
                    canvas.draw()

                    #time.sleep(root.camera_object.update_frequency/1000)
                except Exception as e:
                    root.camera_object.updating = False
                    root.log.log_event("Camera Update Error: " + str(e))
                    pass
            else:
                root.toggle_camera_var.set(0) # if camera is closed by other means than toggle button

def zoom(event, ax, camera_object):
    original_xlim = tuple(camera_object.original_xlim)
    original_ylim = tuple(camera_object.original_ylim)
    
    if event.inaxes is False:
        return
    
    base_scale = 1.1
    if event.button == 'up':
        # Zoom in
        scale_factor = 1 / base_scale
    elif event.button == 'down':
        # Zoom out
        scale_factor = base_scale
    else:
        # No zoom
        scale_factor = 1

    cur_xlim = ax.get_xlim()
    cur_ylim = ax.get_ylim()

    xdata = event.xdata  # get event x location
    ydata = event.ydata  # get event y location
    
    # important fix for faulty zoom event data
    if xdata < 2 or ydata < 2:
        #print("event data < 2")
        return
    
        
    if cur_xlim is None or cur_ylim is None or xdata is None or ydata is None:
        #print("Invalid limits or event data: None")
        return

    
    new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
    new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor

    relx = (cur_xlim[1] - xdata) / (cur_xlim[1] - cur_xlim[0])
    rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])

    new_xlim = [xdata - new_width * (1 - relx), xdata + new_width * (relx)]
    new_ylim = [ydata - new_height * (1 - rely), ydata + new_height * (rely)]

    if new_xlim[0] == new_xlim[1] or new_ylim[0] == new_ylim[1]:
        #print("Invalid limits: Singular")
        return
 
 
    # Constrain the new limits to the original limits
    """
    example
    xlim = [0, 1000]
    ylim = [1000, 0]
    """
    
    if (original_xlim is not None) and (original_ylim is not None):
        if new_xlim[0] < original_xlim[0]:
            #print("new_xlim[0] < original_xlim[0]")
            #print(f"{new_xlim[0]:.1f} < {original_xlim[0]:.1f}")
            new_xlim[0] = int(original_xlim[0])

        if new_xlim[1] > original_xlim[1]:
            #print("new_xlim[1] > original_xlim[1]")
            #print(f"{new_xlim[1]:.1f} > {original_xlim[1]:.1f}")
            new_xlim[1] = int(original_xlim[1])
            
        if new_ylim[0] > original_ylim[0]:
            # switch sign because of inverted y axis
            #print("new_ylim[0] > original_ylim[0]")
            #print(f"{new_ylim[0]:.1f} > {original_ylim[0]:.1f}")
            new_ylim[0] = int(original_ylim[0])

        if new_ylim[1] < original_ylim[1]:
            # switch sign because of inverted
            #print("new_ylim[1] < original_ylim[1]")
            #print(f"{new_ylim[1]:.1f} < {original_ylim[1]:.1f}")
            new_ylim[1] = int(original_ylim[1])

    
    camera_object.set_current_limits(new_xlim, new_ylim)
    #print(f"New limits: {new_xlim}, {new_ylim}")
    
    ax.set_xlim(new_xlim)
    ax.set_ylim(new_ylim)
    ax.figure.canvas.draw()

def reset_zoom(ax, camera_object):
    ax.set_xlim(camera_object.original_xlim)
    ax.set_ylim(camera_object.original_ylim)

    camera_object.set_current_limits(camera_object.original_xlim, camera_object.original_ylim)

    ax.figure.canvas.draw()

def draw_calibration(root, image):
    
    # termination criteria
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    
    # Prepare object points (0,0,0), (1,0,0), (2,0,0), ..., (6,5,0)
    objp = np.zeros((root.camera_object.checkerboard_dimensions[0] * root.camera_object.checkerboard_dimensions[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:root.camera_object.checkerboard_dimensions[0], 0:root.camera_object.checkerboard_dimensions[1]].T.reshape(-1, 2)
    
    # Arrays to store object points and image points from all the images.
    objpoints = [] # 3d point in real world space
    imgpoints = [] # 2d points in image plane.
    

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Find the chess board corners
    ret, corners = cv2.findChessboardCorners(gray, root.camera_object.checkerboard_dimensions, None)

    # If found, add object points, image points (after refining them)
    if ret == True:
        objpoints.append(objp)

        corners2 = cv2.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
        imgpoints.append(corners2)

        # Draw and display the corners
        cv2.drawChessboardCorners(image, root.camera_object.checkerboard_dimensions, corners2, ret)

    return image