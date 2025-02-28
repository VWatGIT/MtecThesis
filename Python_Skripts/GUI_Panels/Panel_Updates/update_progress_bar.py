def update_progress_bar(root, event=None):
    tab = root.tab_group.nametowidget(root.tab_group.select())
    measurements_done = int(tab.measurement_id_var.get()) + 1

    progress_bar = root.new_measurement_panel.nametowidget("progress_bar")

    progress_bar["value"] = measurements_done
    progress_bar.update_idletasks()