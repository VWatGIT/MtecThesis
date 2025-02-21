import tkinter as tk
from tkinter import filedialog

from Function_Groups.data_handling import load_data
from GUI_Panels.Panel_Updates.panel_visibility import show_home_panel
from GUI_Panels.Panel_Updates.update_tab import update_tab
from GUI_Panels.Panel_Updates.update_measurement_info_frame import update_measurement_info_frame 

class LoadMeasurementPanel:
    def __init__(self, parent, root):
        self.root = root

        self.frame = tk.Frame(parent)
        self.tab_group_object = root.tab_group_object

        self.root.load_measurement_panel = self.frame

        load_button = tk.Button(self.frame, text="LOAD", command= lambda: self.load_button_pushed, width=20, height=3)
        load_button.pack(pady=30)

        return_button = tk.Button(self.frame, text="Return", command=lambda: show_home_panel, width=20, height=3)
        return_button.pack(pady=30)

    def load_button_pushed(self):
        self.root.log.log_event("Loading Data")
        file_path = filedialog.askopenfilename(filetypes=[("hdf5 files", "*.h5")])
        if file_path:
            data = load_data(file_path)
            

            self.root.tab_group.create_tab(data)
            update_tab(self.root)
            update_measurement_info_frame(self.root)

            self.measurement_points = data["3D"]["measurement_points"] # TODO also attach this to tab?
            self.current_measurement_id = 0

            tab_name = self.root.tab_group.select()
            tab = self.root.nametowidget(tab_name)

            subtab_group = tab.nametowidget("subtab_group")
            sensor_path_frame = subtab_group.nametowidget("sensor_path_frame")

            measurement_slider = sensor_path_frame.nametowidget("sensor_info_frame").nametowidget("measurement_slider")
            measurement_slider.config(to=self.measurement_points)
            measurement_slider.set(self.current_measurement_id+1)


            vertical_slice_slider = subtab_group.nametowidget("results_frame").nametowidget("slice_plot_frame").nametowidget("vertical_slice_slider")
            vertical_slice_slider.config(from_=1, to=len(data['Visualization']["Slices"]['vertical']), state="normal")
            
            horizontal_slice_slider = subtab_group.nametowidget("results_frame").nametowidget("slice_plot_frame").nametowidget("horizontal_slice_slider")
            horizontal_slice_slider.config(from_=1, to=len(data['Visualization']["Slices"]['horizontal']), state="normal")

            self.update_beam_plot()
            self.root.log.log_event(f"Data loaded from {file_path}")

if __name__ == "__main__":
    root = tk.Tk()
    frame = LoadMeasurementPanel(root, root).frame
    frame.pack()
    root.mainloop()