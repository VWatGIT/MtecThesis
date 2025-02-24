def update_progress_bar(progress_bar, measurements_done, event=None):
    
    progress_bar["value"] = measurements_done
    progress_bar.update_idletasks()