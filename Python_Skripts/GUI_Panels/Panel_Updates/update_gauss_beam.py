def update_gauss_beam(root):
    alpha = float(root.new_measurement_panel.nametowidget("simulation_frame").nametowidget("alpha_entry").get())
    beta = float(root.new_measurement_panel.nametowidget("simulation_frame").nametowidget("beta_entry").get())
    root.gauss_beam.set_Trj(alpha, beta)
    root.gauss_beam.w_0 = float(root.new_measurement_panel.nametowidget("simulation_frame").nametowidget("w_0_entry").get())*1e-3
    root.gauss_beam.wavelength = float(root.new_measurement_panel.nametowidget("simulation_frame").nametowidget("wavelength_entry").get())*1e-9
    root.gauss_beam.I_0 = float(root.new_measurement_panel.nametowidget("simulation_frame").nametowidget("i_0_entry").get())
    