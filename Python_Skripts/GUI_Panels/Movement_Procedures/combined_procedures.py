import threading

from Python_Skripts.GUI_Panels.Movement_Procedures.run_measurements import run_measurements
from Python_Skripts.GUI_Panels.Movement_Procedures.find_beam_centers import find_beam_centers
from Python_Skripts.GUI_Panels.Movement_Procedures.process_data import process_data

from Python_Skripts.Function_Groups.data_handling import autosave

from Python_Skripts.Function_Groups.trajectory import calculate_beam_trajectory_LR, calculate_angles

def combined_procedures(root):
    
    # Move to starting position
    # TODO move to starting position

    root.log.log_event("Starting Search for Beam Centers")
    centers = find_beam_centers(root)
    root.log.log_event("Finished Search for Beam Centers")


    # Now calculate the trajectory
    root.log.log_event("Calculating Trajectory")
    trj = calculate_beam_trajectory_LR(centers)
    angles = calculate_angles(trj)
    # TODO save in data
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




  
