import time
from Python_Skripts.Function_Groups.marker_detection import detect_markers
from Python_Skripts.Function_Groups.probe_tip_detection import draw_probe_tip


def update_camera(root):      
        if root.camera.IsOpen() and root.updating:
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
                
            if root.draw_probe_tip_var.get() == 1:
                image = draw_probe_tip(image, root.probe.probe_tip_position_in_camera_image)

            if root.draw_checkerboard_var.get() == 1:
                image = root.camera_calibration_object.draw_calibration(image)


            # Update Camera Image
            canvas = root.camera_plot_frame.canvas
            ax = canvas.figure.axes[0]
            
            ax.clear()
            ax.imshow(image)
            canvas.draw()

            # update again
            update_frequency = root.camera_object.update_frequency
            try:
                root.after(update_frequency, update_camera(root))
            except Exception as e:
                root.updating = False
                pass
        else:
            root.toggle_camera_var.set(0) 
        # Draw the calibration image with the checkerboard
       