import tkinter as tk


def show_home_panel(root):
    hide_all_panels()
    root.home_panel.place(relx=0, rely=0, anchor="nw", relheight=1, relwidth=1)

def show_new_measurement_panel(root):
    hide_all_panels()
    show_tabgroup()
    root.new_measurement_panel.place(relx=0, rely=0, anchor="nw", relheight=1, relwidth=1)

def show_load_measurement_panel(root):
    hide_all_panels()
    show_tabgroup()
    root.load_measurement_panel.place(relx=0, rely=0, anchor="nw", relheight=1, relwidth=1)

def show_camera_panel(root):
    root.help_panel.place_forget()
    root.camera_panel.place(relx=0, rely=0, anchor="nw", relheight=1, relwidth=1)

def show_help_panel(root):
    root.camera_panel.place_forget()
    root.help_panel.place(relx=0, rely=0, anchor="nw", relheight=1, relwidth=1)

def show_tabgroup(root):



    root.help_panel.place_forget()
    root.camera_panel.place_forget()
    root.tab_group.place(relx=0, rely=0, anchor="nw", relheight=1, relwidth=1)

def hide_all_panels(root):
    

    root.home_panel.place_forget()
    root.new_measurement_panel.place_forget()
    root.load_measurement_panel.place_forget()
    root.camera_panel.place_forget()
    root.help_panel.place_forget()


