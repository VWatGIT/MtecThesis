from Python_Skripts.Function_Groups.position_calculation import relative_hexapod_delta_position



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
    sensor = root.sensor
    probe = root.probe
    hexapod = root.hexapod
    
    
    photo_diode_array_position = sensor.apply_unique_tvecs()
    probe_tip_position = probe.probe_tip_position # Unique tvecs already applied when saving probe tip position
    delta_position = relative_hexapod_delta_position(probe_tip_position, photo_diode_array_position)

    if delta_position[0] >= root.hexapod.travel_ranges["X"] or delta_position[1] >= root.hexapod.travel_ranges["Y"] or delta_position[2] >= root.hexapod.travel_ranges["Z"]:
        root.log.log_event("Error: Movement too large")


    rcv = hexapod.move(delta_position, flag = "relative")
    root.log.log_event(rcv)
    
    

if __name__ == "__main__":
    from Python_Skripts.Function_Groups.hexapod import Hexapod
    from Python_Skripts.Function_Groups.sensor import Sensor
    from Python_Skripts.Function_Groups.probe import Probe
    from Python_Skripts.Function_Groups.camera import Camera    
    


