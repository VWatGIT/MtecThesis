def update_progress_bar(self, progress_bar, measurements_done):
    
    progress_bar["value"] = measurements_done
    progress_bar.update_idletasks()