import tkinter as tk
from tkinter import ttk
import numpy as np

class ManualAdjustPanel:
    def __init__(self, parent, manual_alignment):
        """
        External Functions:
        - manual_alignment(manual_adjust_panel): confirms input and moves hexapod to new position
        """

        self.panel = tk.LabelFrame(parent,text="Adjust Hexapod Positon",name="panel")
        self.panel.pack(side="left", expand=True)

        for i in range(10):
            self.panel.grid_rowconfigure(i, weight=1)
        for i in range(4):
            self.panel.grid_columnconfigure(i, weight=1)

        e_width = 10

        hexapod_x_label = tk.Label(self.panel, text="X: ", name="hexapod_x_label")
        hexapod_x_label.grid(row=0, column=0, pady=5, sticky="e")
        self.hexapod_x_entry = tk.Entry(self.panel, width=e_width, name="hexapod_x_entry")
        self.hexapod_x_entry.grid(row=0, column=1, pady=5, sticky="w")
        self.hexapod_x_entry.insert(0, "0")

        hexapod_y_label = tk.Label(self.panel, text="Y: ", name="hexapod_y_label")
        hexapod_y_label.grid(row=1, column=0, pady=5, sticky="e")
        self.hexapod_y_entry = tk.Entry(self.panel, width=e_width, name="hexapod_y_entry")
        self.hexapod_y_entry.grid(row=1, column=1, pady=5, sticky="w")
        self.hexapod_y_entry.insert(0, "0")

        hexapod_z_label = tk.Label(self.panel, text="Z: ", name="hexapod_z_label")
        hexapod_z_label.grid(row=2, column=0, pady=5, sticky="e")
        self.hexapod_z_entry = tk.Entry(self.panel, width=e_width, name = "hexapod_z_entry")
        self.hexapod_z_entry.grid(row=2, column=1, pady=5, sticky="w")
        self.hexapod_z_entry.insert(0, "0")

        seperator = ttk.Separator(self.panel, orient="horizontal")
        seperator.grid(row=3, column=0, columnspan=4, sticky="ew", pady=5)

        hexapod_U_label = tk.Label(self.panel, text="U: ", name="hexapod_U_label")
        hexapod_U_label.grid(row=4, column=0, pady=5, sticky="e")
        self.hexapod_U_entry = tk.Entry(self.panel, width=e_width, name = "hexapod_U_entry")
        self.hexapod_U_entry.grid(row=4, column=1, pady=5, sticky="w")
        self.hexapod_U_entry.insert(0, "0")

        hexapod_V_label = tk.Label(self.panel, text="V: ", name="hexapod_V_label")
        hexapod_V_label.grid(row=5, column=0, pady=5, sticky="e")
        self.hexapod_V_entry = tk.Entry(self.panel, width=e_width, name = "hexapod_V_entry")
        self.hexapod_V_entry.grid(row=5, column=1, pady=5, sticky="w")
        self.hexapod_V_entry.insert(0, "0")

        hexapod_W_label = tk.Label(self.panel, text="W: ", name="hexapod_W_label")
        hexapod_W_label.grid(row=6, column=0, pady=5, sticky="e")
        self.hexapod_W_entry = tk.Entry(self.panel, width=e_width, name = "hexapod_W_entry")
        self.hexapod_W_entry.grid(row=6, column=1, pady=5, sticky="w")
        self.hexapod_W_entry.insert(0, "0")

        # Increment Buttons
        hexapod_x_increment_button = self.create_increment_button(self.panel, self.hexapod_x_entry, 0.1)
        hexapod_x_increment_button.grid(row=0, column=2, pady=5, sticky="w")
        hexapod_x_decrement_button = self.create_increment_button(self.panel, self.hexapod_x_entry, -0.1)
        hexapod_x_decrement_button.grid(row=0, column=3, pady=5, sticky="w")

        hexapod_y_increment_button = self.create_increment_button(self.panel, self.hexapod_y_entry, 0.1)
        hexapod_y_increment_button.grid(row=1, column=2, pady=5, sticky="w")
        hexapod_y_decrement_button = self.create_increment_button(self.panel, self.hexapod_y_entry, -0.1)
        hexapod_y_decrement_button.grid(row=1, column=3, pady=5, sticky="w")

        hexapod_z_increment_button = self.create_increment_button(self.panel, self.hexapod_z_entry, 0.1)
        hexapod_z_increment_button.grid(row=2, column=2, pady=5, sticky="w")
        hexapod_z_decrement_button = self.create_increment_button(self.panel, self.hexapod_z_entry, -0.1)
        hexapod_z_decrement_button.grid(row=2, column=3, pady=5, sticky="w")

        hexapod_U_increment_button = self.create_increment_button(self.panel, self.hexapod_U_entry, 0.1)
        hexapod_U_increment_button.grid(row=4, column=2, pady=5, sticky="w")
        hexapod_U_decrement_button = self.create_increment_button(self.panel, self.hexapod_U_entry, -0.1)
        hexapod_U_decrement_button.grid(row=4, column=3, pady=5, sticky="w")

        hexapod_V_increment_button = self.create_increment_button(self.panel, self.hexapod_V_entry, 0.1)
        hexapod_V_increment_button.grid(row=5, column=2, pady=5, sticky="w")
        hexapod_V_decrement_button = self.create_increment_button(self.panel, self.hexapod_V_entry, -0.1)
        hexapod_V_decrement_button.grid(row=5, column=3, pady=5, sticky="w")

        hexapod_W_increment_button = self.create_increment_button(self.panel, self.hexapod_W_entry, 0.1)
        hexapod_W_increment_button.grid(row=6, column=2, pady=5, sticky="w")
        hexapod_W_decrement_button = self.create_increment_button(self.panel, self.hexapod_W_entry, -0.1)
        hexapod_W_decrement_button.grid(row=6, column=3, pady=5, sticky="w")

        seperator2 = ttk.Separator(self.panel, orient="horizontal")
        seperator2.grid(row=7, column=0, columnspan=4, sticky="ew", pady=5)

        set_to_0_button = tk.Button(self.panel, text="Set 0", command=self.set_to_0)
        set_to_0_button.grid(row=8, column=3,columnspan=2,rowspan=2, pady=5, sticky="w")

        self.relative_checkbutton_var = tk.IntVar(name="relative_checkbutton_var")
        self.relative_checkbutton_var.set(0)

        self.relative_checkbutton = tk.Checkbutton(self.panel, text="Relative", name="relative_checkbutton_var", variable=self.relative_checkbutton_var)
        self.relative_checkbutton.grid(row=8, column=0,columnspan=2,pady=5, sticky="ns")
        #self.relative_checkbutton.rowconfigure(8, weight=100)

        manual_align_button = tk.Button(self.panel, text="Confirm", command=manual_alignment(self.panel))
        manual_align_button.grid(row=9, column=0, columnspan= 2, pady=5, sticky="ns")
        #self.panel.rowconfigure(8, weight=100)

    def create_increment_button(self, parent, entry_field, increment):
        def increment_entry(entry_field, increment):
            current_value = entry_field.get()
            new_value = round(float(current_value) + increment, 4)

            entry_field.delete(0, "end")
            entry_field.insert(0, str(new_value))
        
        if np.sign(increment) > 0:
            increment_button = tk.Button(parent, text=f"+{increment}", command=lambda: increment_entry(entry_field, increment))
        else:
            increment_button = tk.Button(parent, text=f"{increment}", command=lambda: increment_entry(entry_field, increment))
        
        return increment_button

    def set_to_0(self):
        self.hexapod_x_entry.delete(0, "end")
        self.hexapod_x_entry.insert(0, "0")
        self.hexapod_y_entry.delete(0, "end")
        self.hexapod_y_entry.insert(0, "0")
        self.hexapod_z_entry.delete(0, "end")
        self.hexapod_z_entry.insert(0, "0")
        self.hexapod_U_entry.delete(0, "end")
        self.hexapod_U_entry.insert(0, "0")
        self.hexapod_V_entry.delete(0, "end")
        self.hexapod_V_entry.insert(0, "0")
        self.hexapod_W_entry.delete(0, "end")
        self.hexapod_W_entry.insert(0, "0")