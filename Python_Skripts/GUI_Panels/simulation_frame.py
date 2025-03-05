import tkinter as tk

class Simulation_Frame:
    def __init__(self, parent, root):
        self.root = root
        
        self.frame = tk.LabelFrame(parent, text="Simulation Parameters", name="simulation_frame")
        
        self.simulate_var = tk.IntVar(value = 1) # TODO change to 0
        self.root.simulate_var = self.simulate_var # add to root for access in other functions
       

        checkbox_panel_object = self.root.checkbox_panel_object


        wavelength_label = tk.Label(self.frame, text="Wavelength [nm]:")
        w_0_label = tk.Label(self.frame, text="Beam Waist [mm]:")
        i_0_label = tk.Label(self.frame, text="I_0 [W/m^2]:")
        alpha_label = tk.Label(self.frame, text="Simulate Pitch [deg]:")
        beta_label = tk.Label(self.frame, text="Simulate Yaw [deg]:")

        self.wavelength_entry = tk.Entry(self.frame, name="wavelength_entry", width=10)
        self.w_0_entry = tk.Entry(self.frame, name="w_0_entry", width=10)
        self.i_0_entry = tk.Entry(self.frame, name="i_0_entry", width=10)
        self.alpha_entry = tk.Entry(self.frame, name="alpha_entry", width=10)
        self.beta_entry = tk.Entry(self.frame, name="beta_entry", width=10)

        self.wavelength_entry.insert(0, "1300")
        self.w_0_entry.insert(0, "1")
        self.i_0_entry.insert(0, "60000")
        self.alpha_entry.insert(0, "0")
        self.beta_entry.insert(0, "0")

        self.simulate_checkbox = tk.Checkbutton(self.frame, text="Simulation Active", name="simulate_checkbox", variable=self.simulate_var, command = lambda: checkbox_panel_object.grey_out(flag = True))
        seperator = tk.ttk.Separator(self.frame, orient="horizontal")

        for i in range(7):
            self.frame.grid_rowconfigure(i, weight=1)
        for i in range(2):
            self.frame.grid_columnconfigure(i, weight=0)

        self.frame.grid_columnconfigure(1, weight=1)

        self.simulate_checkbox.grid(row = 0, column=0, columnspan=1, pady=5, sticky="w")
        seperator.grid(row=1, column=0, columnspan=2, pady= 5, sticky="ew")
        
        wavelength_label.grid(row=2, column=0, pady=5, sticky="w")
        w_0_label.grid(row=3, column=0, pady=5, sticky="w")
        i_0_label.grid(row=4, column=0, pady=5, sticky="w")
        alpha_label.grid(row=5, column=0, pady=5, sticky="w")
        beta_label.grid(row=6, column=0, pady=5, sticky="w")



        self.wavelength_entry.grid(row=2, column=1, pady=5, sticky="w")
        self.w_0_entry.grid(row=3, column=1, pady=5, sticky="w")
        self.i_0_entry.grid(row=4, column=1, pady=5, sticky="w")
        self.alpha_entry.grid(row=5, column=1, pady=5, sticky="w")
        self.beta_entry.grid(row=6, column=1, pady=5, sticky="w")
