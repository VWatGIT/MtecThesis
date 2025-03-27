import tkinter as tk
from tkinter import ttk
import numpy as np
import threading

from Python_Skripts.GUI_Panels.Movement_Procedures.alignment import alignment, determine_automatic_alignment

class ManualAdjustPanel:
    def __init__(self, parent, root):
        """
        External Functions:
        - manual_alignment(manual_adjust_panel): confirms input and moves hexapod to new position
        """
        self.root = root

        self.panel = tk.LabelFrame(parent,text="Adjust Hexapod Positon",name="panel")

        self.root.manual_adjust_panel = self.panel

        for i in range(10):
            self.panel.grid_rowconfigure(i, weight=1)
        for i in range(4):
            self.panel.grid_columnconfigure(i, weight=1)

        self.panel.grid_columnconfigure(0, weight=10, minsize=50)
        self.panel.grid_columnconfigure(1, weight=10, minsize=50)
        self.panel.grid_columnconfigure(2, weight=1)
        self.panel.grid_columnconfigure(3, weight=1)
        
        e_width = 10
    
        determine_automatic_alignment_button = tk.Button(self.panel, text="Automatic Determination", command= lambda: determine_automatic_alignment(self.root))
        manual_align_checkbutton = tk.Checkbutton(self.panel, text="Manual", variable = self.root.manual_alignment_var, command= lambda: root.checkbox_panel_object.grey_out())
        seperator3 = ttk.Separator(self.panel, orient="horizontal")

        determine_automatic_alignment_button.grid(row=0, column=0, columnspan=2, pady=5, sticky="nsew")
        manual_align_checkbutton.grid(row=0, column=2, columnspan=2, pady=5, sticky="nsew")

        seperator3.grid(row=1, column=0, columnspan=4, sticky="ew", pady=5)


        hexapod_x_label = tk.Label(self.panel, text="X: ", name="hexapod_x_label")
        hexapod_x_label.grid(row=2, column=0, pady=5, sticky="e")
        self.hexapod_x_entry = tk.Entry(self.panel, width=e_width, name="hexapod_x_entry")
        self.hexapod_x_entry.grid(row=2, column=1, pady=5, sticky="w")
        self.hexapod_x_entry.insert(0, "0")

        hexapod_y_label = tk.Label(self.panel, text="Y: ", name="hexapod_y_label")
        hexapod_y_label.grid(row=3, column=0, pady=5, sticky="e")
        self.hexapod_y_entry = tk.Entry(self.panel, width=e_width, name="hexapod_y_entry")
        self.hexapod_y_entry.grid(row=3, column=1, pady=5, sticky="w")
        self.hexapod_y_entry.insert(0, "0")

        hexapod_z_label = tk.Label(self.panel, text="Z: ", name="hexapod_z_label")
        hexapod_z_label.grid(row=4, column=0, pady=5, sticky="e")
        self.hexapod_z_entry = tk.Entry(self.panel, width=e_width, name = "hexapod_z_entry")
        self.hexapod_z_entry.grid(row=4, column=1, pady=5, sticky="w")
        self.hexapod_z_entry.insert(0, "0")

        hexapod_U_label = tk.Label(self.panel, text="U: ", name="hexapod_U_label")
        hexapod_U_label.grid(row=5, column=0, pady=5, sticky="e")
        self.hexapod_U_entry = tk.Entry(self.panel, width=e_width, name = "hexapod_U_entry")
        self.hexapod_U_entry.grid(row=5, column=1, pady=5, sticky="w")
        self.hexapod_U_entry.insert(0, "0")

        hexapod_V_label = tk.Label(self.panel, text="V: ", name="hexapod_V_label")
        hexapod_V_label.grid(row=6, column=0, pady=5, sticky="e")
        self.hexapod_V_entry = tk.Entry(self.panel, width=e_width, name = "hexapod_V_entry")
        self.hexapod_V_entry.grid(row=6, column=1, pady=5, sticky="w")
        self.hexapod_V_entry.insert(0, "0")

        hexapod_W_label = tk.Label(self.panel, text="W: ", name="hexapod_W_label")
        hexapod_W_label.grid(row=7, column=0, pady=5, sticky="e")
        self.hexapod_W_entry = tk.Entry(self.panel, width=e_width, name = "hexapod_W_entry")
        self.hexapod_W_entry.grid(row=7, column=1, pady=5, sticky="w")
        self.hexapod_W_entry.insert(0, "0")

        # Increment Buttons
        hexapod_x_increment_button = self.create_increment_button(self.panel, self.hexapod_x_entry, 0.1)
        hexapod_x_increment_button.grid(row=2, column=2, pady=5, sticky="w")
        hexapod_x_decrement_button = self.create_increment_button(self.panel, self.hexapod_x_entry, -0.1)
        hexapod_x_decrement_button.grid(row=2, column=3, pady=5, sticky="w")

        hexapod_y_increment_button = self.create_increment_button(self.panel, self.hexapod_y_entry, 0.1)
        hexapod_y_increment_button.grid(row=3, column=2, pady=5, sticky="w")
        hexapod_y_decrement_button = self.create_increment_button(self.panel, self.hexapod_y_entry, -0.1)
        hexapod_y_decrement_button.grid(row=3, column=3, pady=5, sticky="w")

        hexapod_z_increment_button = self.create_increment_button(self.panel, self.hexapod_z_entry, 0.1)
        hexapod_z_increment_button.grid(row=4, column=2, pady=5, sticky="w")
        hexapod_z_decrement_button = self.create_increment_button(self.panel, self.hexapod_z_entry, -0.1)
        hexapod_z_decrement_button.grid(row=4, column=3, pady=5, sticky="w")

        hexapod_U_increment_button = self.create_increment_button(self.panel, self.hexapod_U_entry, 0.1)
        hexapod_U_increment_button.grid(row=5, column=2, pady=5, sticky="w")
        hexapod_U_decrement_button = self.create_increment_button(self.panel, self.hexapod_U_entry, -0.1)
        hexapod_U_decrement_button.grid(row=5, column=3, pady=5, sticky="w")

        hexapod_V_increment_button = self.create_increment_button(self.panel, self.hexapod_V_entry, 0.1)
        hexapod_V_increment_button.grid(row=6, column=2, pady=5, sticky="w")
        hexapod_V_decrement_button = self.create_increment_button(self.panel, self.hexapod_V_entry, -0.1)
        hexapod_V_decrement_button.grid(row=6, column=3, pady=5, sticky="w")

        hexapod_W_increment_button = self.create_increment_button(self.panel, self.hexapod_W_entry, 0.1)
        hexapod_W_increment_button.grid(row=7, column=2, pady=5, sticky="w")
        hexapod_W_decrement_button = self.create_increment_button(self.panel, self.hexapod_W_entry, -0.1)
        hexapod_W_decrement_button.grid(row=7, column=3, pady=5, sticky="w")

        seperator2 = ttk.Separator(self.panel, orient="horizontal")
        seperator2.grid(row=8, column=0, columnspan=4, sticky="ew", pady=5)

        set_to_0_button = tk.Button(self.panel, text="Set 0", command= self.set_to_0)
        set_to_0_button.grid(row=9, column=3,columnspan=1,rowspan=2, pady=5, sticky="w")

        self.relative_checkbutton_var = tk.IntVar(name="relative_checkbutton_var")
        self.relative_checkbutton_var.set(0)

        self.panel.relative_checkbutton_var = self.relative_checkbutton_var

        self.relative_checkbutton = tk.Checkbutton(self.panel, text="Relative", name="relative_checkbutton", variable=self.relative_checkbutton_var)
        self.relative_checkbutton.grid(row=9, column=2,columnspan=1,pady=5, sticky="w")
        #self.relative_checkbutton.rowconfigure(8, weight=100)

        align_button = tk.Button(self.panel, text="Confirm", command= self.start_alignment)
        align_button.grid(row=9, column=0, columnspan= 2, pady=5, padx = 10, sticky="nsew")
        #self.panel.rowconfigure(8, weight=100)


    def start_alignment(self):
        alignment_thread = threading.Thread(target= lambda: alignment(self.root))
        self.root.thread_list.append(alignment_thread)
        alignment_thread.start()

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


if __name__ == "__main__":
    from Python_Skripts.Function_Groups.hexapod import Hexapod
    from Python_Skripts.GUI import UserInterface


    root = tk.Tk()

    app = UserInterface(root, test_mode = True)
    
    root.hexapod.connect_sockets()

    manual_adjust_panel = ManualAdjustPanel(root, root).panel
    manual_adjust_panel.pack(side = "top", fill = "none")
    root.mainloop()
