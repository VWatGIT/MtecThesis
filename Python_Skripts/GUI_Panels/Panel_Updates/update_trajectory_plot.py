from GUI_Panels.Panel_Updates.update_trajectory_plot import plot_alpha_beta
# TODO not needed?
def update_trajectory_plot(root, event = None):
    tab_name = root.tab_group.select()
    tab = root.tab_group.nametowidget(tab_name)
    data = tab.data

    subtab_group = tab.nametowidget("subtab_group")
    results_frame = subtab_group.nametowidget("results_frame")
    trajectory_plot_frame = results_frame.nametowidget("trajectory_plot_frame")

    canvas = trajectory_plot_frame.canvas
    ax = canvas.figure.axes[0]
    
    plot_alpha_beta(data, ax)