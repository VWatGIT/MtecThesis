import threading

from Python_Skripts.GUI_Panels.Movement_Procedures.run_measurements import run_measurements
from Python_Skripts.GUI_Panels.Movement_Procedures.find_beam_centers import find_beam_centers
from Python_Skripts.GUI_Panels.Movement_Procedures.process_data import process_data, process_beam_centers

from Python_Skripts.Function_Groups.data_handling import autosave


def combined_procedures(root):
    
    rcv = root.hexapod.move_to_default_position() # Move to default position
    root.log.log_event(rcv)

    if root.skip_center_search_var.get() == 0:
            
        root.log.log_event("Starting Search for Beam Centers")
        centers = find_beam_centers(root)
        root.log.log_event(f"Finished Search for Beam Centers: {centers}")

        # Now calculate the trajectory
        root.log.log_event("Calculating Trajectory")
        trj, angles = process_beam_centers(root)
        root.log.log_event(f"Trajectory: {trj}, Angles: {angles}")

        # Now align the probe with sensor in an angle
        
        # TODO align probe with sensor again

    # Now start the measurements
    root.log.log_event("Started Measurements")
    run_measurements(root)
    root.log.log_event("Done with measurements")  

    # Move to default position  
    if root.hexapod.connection_status is True:
        root.hexapod.move_to_default_position() 
        root.log.log_event("Moved Hexapod to default position")


    # Process the data
    root.log.log_event("Processing data")
    process_data(root)
    root.log.log_event("Done processing data")

    autosave(root)
    root.new_measurement_panel.nametowidget("save_button").config(state="normal")
    root.measurement_running = False # Measurement is done




  
