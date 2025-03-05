import tkinter as tk

class Simulation_Frame:
    def __init__(self, parent, root):
        self.root = root
        
        self.frame = tk.LabelFrame(parent, text="Simulation Settings", name="simulation_frame")
        
        self.simulate_var = tk.IntVar(value = 1) # TODO change to 0
        self.root.simulate_var = self.simulate_var # add to root for access in other functions
       
        wavelength_label = tk.Label(self.frame, text="Wavelength [nm]:")
        w_0_label = tk.Label(self.frame, text="Beam Waist [mm]:")
        i_0_label = tk.Label(self.frame, text="I_0 [W/m^2]:")
        theta_label = tk.Label(self.frame, text="Simulate Pitch [deg]:")
        phi_label = tk.Label(self.frame, text="Simulate Yaw [deg]:")

        self.wavelength_entry = tk.Entry(self.frame, name="wavelength_entry")
        self.w_0_entry = tk.Entry(self.frame, name="w_0_entry")
        self.i_0_entry = tk.Entry(self.frame, name="i_0_entry")
        self.theta_entry = tk.Entry(self.frame, name="theta_entry")
        self.phi_entry = tk.Entry(self.frame, name="phi_entry")

        self.wavelength_entry.insert(0, "1300")
        self.w_0_entry.insert(0, "1")
        self.i_0_entry.insert(0, "60000")
        self.theta_entry.insert(0, "0")
        self.phi_entry.insert(0, "0")

        self.simulate_checkbox = tk.Checkbutton(self.frame, text="Simulation Active", name="simulate_checkbox", variable=self.simulate_var)

        for i in range(6):
            self.frame.grid_rowconfigure(i, weight=1)
        for i in range(2):
            self.frame.grid_columnconfigure(i, weight=1)

        self.simulate_checkbox.grid(row = 0, column=0, columnspan=2, pady=5, sticky="ew")
        
        wavelength_label.grid(row=1, column=0, pady=5, sticky="e")
        w_0_label.grid(row=2, column=0, pady=5, sticky="e")
        i_0_label.grid(row=3, column=0, pady=5, sticky="e")
        theta_label.grid(row=4, column=0, pady=5, sticky="e")
        phi_label.grid(row=5, column=0, pady=5, sticky="e")



        self.wavelength_entry.grid(row=1, column=1, pady=5, sticky="w")
        self.w_0_entry.grid(row=2, column=1, pady=5, sticky="w")
        self.i_0_entry.grid(row=3, column=1, pady=5, sticky="w")
        self.theta_entry.grid(row=4, column=1, pady=5, sticky="w")
        self.phi_entry.grid(row=5, column=1, pady=5, sticky="w")
