
# Update mechanism is unnecessary, better option would be to use tk variables in the objects and update them directly
def update_checkboxes(root):
    if root.stop_update_checkboxes is True:
        return
    
    if root.camera_object.camera_connected is True:
        root.checkbox_vars["camera_connected"].set(1)
    else:
        root.checkbox_vars["camera_connected"].set(0)

    if root.camera_object.camera_calibrated is True:
        root.checkbox_vars["camera_calibrated"].set(1)
    else:
        root.checkbox_vars["camera_calibrated"].set(0)

    if root.probe.marker_detected is True and root.sensor.marker_detected is True:
        root.checkbox_vars["markers_detected"].set(1)
    else:
        root.checkbox_vars["markers_detected"].set(0)

    if root.probe.probe_detected is True:
        root.checkbox_vars["probe_detected"].set(1)
    else:
        root.checkbox_vars["probe_detected"].set(0)

    if root.hexapod.connection_status is True:
        root.checkbox_vars["hexapod_connected"].set(1)
    else:
        root.checkbox_vars["hexapod_connected"].set(0)

    if root.sensor.stage is not None:
        root.checkbox_vars["stage_connected"].set(1)
    else:
        root.checkbox_vars["stage_connected"].set(0)

    root.after(500, update_checkboxes, root)
    #TODO: fix this, its crashing the ui 

def check_checkboxes(root):
    ready = True
    if root.simulate_var.get() == True:
        ready = True
        root.log.log_event("Simulation Mode Active")
        return ready

    if root.manual_alignment_var.get() == True:
        if not root.checkbox_vars["hexapod_connected"].get() or not root.checkbox_vars['stage_connected'].get():
            ready = False
    else:
        for key in root.checkbox_vars.keys():
            if root.checkbox_vars[key].get() != 1:
                ready = False
                root.log.log_event(f"{key} not ready")
                
    if ready:
        root.log.log_event("All Systems Ready")
    else:
        root.log.log_event("Not all Systems Ready")

    return ready
            