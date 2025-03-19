import threading

from Python_Skripts.GUI_Panels.Movement_Procedures.run_measurements import run_measurements
from Python_Skripts.GUI_Panels.Movement_Procedures.find_beam_centers import find_beam_centers
from Python_Skripts.GUI_Panels.Movement_Procedures.process_data import process_data, process_beam_centers

from Python_Skripts.Function_Groups.data_handling import autosave


def combined_procedures(root):
   
    if root.center_search_var.get() == True:
            
        root.log.log_event("Starting Search for Beam Centers")
        centers = find_beam_centers(root)
        root.log.log_event(f"Finished Search for Beam Centers: {centers}")

        # Now calculate the trajectory
        root.log.log_event("Calculating Trajectory")
        trj, angles = process_beam_centers(root)
        root.log.log_event(f"Trajectory: {trj}, Angles: {angles}")

        # Now align the probe with sensor in an angle
        # TODO implement angled alignment
        # Alignment finished
        
    else:
        root.log.log_event("Skipping Center Search")

    if root.box_measurements_var.get() == True:
        # Now start the measurements
        root.log.log_event("Started Measurements")
        run_measurements(root)
        root.log.log_event("Done with measurements")  

        # Process the data
        root.log.log_event("Processing data")
        process_data(root)
        root.log.log_event("Done processing data")
    else:
        root.log.log_event("Skipping Measurements")


    # Move to default position  
    if root.hexapod.connection_status is True:
        rcv = root.hexapod.move_to_default_position() 
        root.log.log_event("rcv")

    autosave(root)
    root.new_measurement_panel.nametowidget("save_button").config(state="normal")
    root.measurement_running = False # Measurement is done





  
