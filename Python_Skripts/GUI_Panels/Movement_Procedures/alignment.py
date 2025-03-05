from Python_Skripts.Function_Groups.position_calculation import translate_marker_vecs_to_position, relative_hexapod_delta_position
def manual_alignment(root):
    manual_adjust_panel = root.manual_adjust_panel
    hexapod = root.hexapod

    # manual alignment for testing
    x = manual_adjust_panel.nametowidget("hexapod_x_entry").get()
    y = manual_adjust_panel.nametowidget("hexapod_y_entry").get()
    z = manual_adjust_panel.nametowidget("hexapod_z_entry").get()
    U = manual_adjust_panel.nametowidget("hexapod_U_entry").get()
    V = manual_adjust_panel.nametowidget("hexapod_V_entry").get()
    W = manual_adjust_panel.nametowidget("hexapod_W_entry").get()

    if manual_adjust_panel.relative_checkbutton_var.get() == 1:
        rcv = hexapod.move((x, y, z, U, V, W), flag = "relative")
    else:
        rcv = hexapod.move((x, y, z, U, V, W), flag = "absolute")
   
    root.log.log_event(rcv)

def automatic_alignment(root):
    # TODO implement automatic alignment
    '''
    photo_diode_position = translate_marker_vecs_to_position(root.sensor.marker_tvecs, root.sensor.marker_rvecs, root.sensor.unique_tvecs, root.sensor.unique_rvecs)
    probe_tip_position = translate_marker_vecs_to_position(root.probe.marker_tvecs, root.probe.marker_rvecs, root.probe.unique_tvecs, root.probe.unique_rvecs)
    '''

    


    root.log.log_event("Automatic Alignment done")
    

if __name__ == "__main__":
    from Python_Skripts.Function_Groups.hexapod import Hexapod
    from Python_Skripts.Function_Groups.sensor import Sensor
    from Python_Skripts.Function_Groups.probe import Probe
    from Python_Skripts.Function_Groups.camera import Camera    
    


