from Python_Skripts.Function_Groups.position_calculation import relative_hexapod_delta_position
import numpy as np


def alignment(root):
    manual_adjust_panel = root.manual_adjust_panel
    hexapod = root.hexapod

    # manual alignment for testing
    x = manual_adjust_panel.nametowidget("hexapod_x_entry").get()
    y = manual_adjust_panel.nametowidget("hexapod_y_entry").get()
    z = manual_adjust_panel.nametowidget("hexapod_z_entry").get()
    U = manual_adjust_panel.nametowidget("hexapod_U_entry").get()
    V = manual_adjust_panel.nametowidget("hexapod_V_entry").get()
    W = manual_adjust_panel.nametowidget("hexapod_W_entry").get()

    new_pos = (float(x), float(y), float(z), float(U), float(V), float(W))

    for i in range(len(new_pos)):
        if new_pos[i] == "":
            root.log.log_event("Error: Empty entry")
            return
        
    # root.hexapod.travel_ranges maybe add warning if out of range
        

    if root.manual_alignment_var.get() == True:
        if manual_adjust_panel.relative_checkbutton_var.get() == 1:
            rcv = hexapod.move((x, y, z, U, V, W), flag = "relative")
        else:
            rcv = hexapod.move((x, y, z, U, V, W), flag = "absolute")
    else:
        rcv = hexapod.move((x, y, z, U, V, W), flag= "absolute")

    root.log.log_event(rcv)

def determine_automatic_alignment(root):

    if root.camera_object.camera_calibrated is False:
        root.log.log_event("Failed: Camera not calibrated")
        return
    if root.probe.probe_tip_position is None:
        root.log.log_event("Failed: Probe Tip not detected/saved")
        return
    if root.probe.marker_detected is False:
        root.log.log_event("Failed: Markers not detected")
        return


    try:
        photo_diode_array_position = root.sensor.apply_unique_tvecs()
        probe_tip_position = root.probe.probe_tip_position # Unique tvecs already applied when saving probe tip position
        delta_pos = relative_hexapod_delta_position(probe_tip_position, photo_diode_array_position)

        # convert to absolute position
        if root.hexapod.connection_status == True:
            old_pos = root.hexapod.get_position()
        else:
            old_pos = root.hexapod.default_position

        new_pos = old_pos + delta_pos


        # Set values in the entries
        manual_adjust_panel = root.manual_adjust_panel
        manual_adjust_panel.nametowidget("hexapod_x_entry").delete(0, "end")
        manual_adjust_panel.nametowidget("hexapod_y_entry").delete(0, "end")
        manual_adjust_panel.nametowidget("hexapod_z_entry").delete(0, "end")
        manual_adjust_panel.nametowidget("hexapod_U_entry").delete(0, "end")
        manual_adjust_panel.nametowidget("hexapod_V_entry").delete(0, "end")
        manual_adjust_panel.nametowidget("hexapod_W_entry").delete(0, "end")

        manual_adjust_panel.nametowidget("hexapod_x_entry").insert(0, f"{new_pos[0]:.2f}")
        manual_adjust_panel.nametowidget("hexapod_y_entry").insert(0, f"{new_pos[1]:.2f}")
        manual_adjust_panel.nametowidget("hexapod_z_entry").insert(0, f"{new_pos[2]:.2f}")
        manual_adjust_panel.nametowidget("hexapod_U_entry").insert(0, f"{new_pos[3]:.2f}")
        manual_adjust_panel.nametowidget("hexapod_V_entry").insert(0, f"{new_pos[4]:.2f}")
        manual_adjust_panel.nametowidget("hexapod_W_entry").insert(0, f"{new_pos[5]:.2f}")

        root.log.log_event(f"Hexapod Alignment Path: [{new_pos[0]:.2f}, {new_pos[1]:.2f}, {new_pos[2]:.2f}, {new_pos[3]:.2f}, {new_pos[4]:.2f}, {new_pos[5]:.2f}]")
    except Exception as e:
        root.log.log_event("Hexapod Alignment Path calculation failed: " + str(e))

    return 
    

if __name__ == "__main__":
    from Python_Skripts.Function_Groups.hexapod import Hexapod
    from Python_Skripts.Function_Groups.sensor import Sensor
    from Python_Skripts.Function_Groups.probe import Probe
    from Python_Skripts.Function_Groups.camera import Camera    
    


    hexapod = Hexapod()
    hexapod.connect_sockets()
    
    print(hexapod.send_command('get_pos'))

    rcv = hexapod.send_command('get_pos')
    old_pos = np.array(list(map(float, rcv.split()))[1:])
    
    print(old_pos)
