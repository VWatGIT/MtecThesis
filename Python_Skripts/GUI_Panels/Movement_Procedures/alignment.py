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
    # add additional arguments
        

    root.log.log_event("Rough Alignment done")
    pass
