from Python_Skripts.GUI_Panels.Panel_Updates.update_beam_plot import update_beam_plot

def update_slice_plot(root, event=None):
    tab_name = root.tab_group.select()
    tab = root.nametowidget(tab_name)

    data = tab.data 

    subtab_group = tab.nametowidget("subtab_group")
    results_frame = subtab_group.nametowidget("results_frame")

    vertical_slice_plot_frame = results_frame.nametowidget("vertical_slice_plot_frame")
    vertical_canvas = vertical_slice_plot_frame.canvas
    vertical_ax = vertical_canvas.figure.axes[0]

    horizontal_slice_plot_frame = results_frame.nametowidget("horizontal_slice_plot_frame")
    horizontal_canvas = horizontal_slice_plot_frame.canvas
    horizontal_ax = horizontal_canvas.figure.axes[0]

    # Interpolation Method with checkbox
    interpolation_method = 'nearest' if root.interpolation_var.get() == 0 else 'gaussian'

    #only update if data is available
    if data["Visualization"]["Slices"]["vertical"] != {}:
        
        # Update the vertical slice plot
        vertical_slice= data['Visualization']["Slices"]['vertical'][str(root.vertical_slice_index_var.get())] # Get the slice data
        heatmap = vertical_slice['heatmap']
        keys = data['Visualization']['Slices']['vertical'].keys()
        first_key = next(iter(keys))
        extent = data['Visualization']['Slices']['vertical'][first_key]['heatmap_extent']


        # Update the vertical slice plot
        vertical_ax.clear()

        cax = vertical_ax.imshow(heatmap,extent=extent, cmap='hot', interpolation=interpolation_method)
        fig = vertical_ax.get_figure()

        # Plot colorbar once
        if not hasattr(vertical_slice_plot_frame, 'check'):
            vertical_slice_plot_frame.check = True
            fig.colorbar(cax, ax=vertical_ax, label='Signal Sum')
        
        vertical_ax.invert_yaxis() # TODO there is some slicing ordering error
        vertical_ax.set_aspect('auto')
        vertical_canvas.draw()

        # Update Beam Plot for Seethrough Planes
        update_beam_plot(root)

    if data["Visualization"]["Slices"]["horizontal"] != {}:

        horizontal_index = str(root.horizontal_slice_index_var.get())
        horizontal_slice = data['Visualization']["Slices"]['horizontal'][horizontal_index] # Get the slice data
        heatmap = horizontal_slice['heatmap']
        extent = data['Visualization']['Slices']['horizontal'][horizontal_index]['heatmap_extent']

        # Update the horizontal slice plot
        horizontal_ax.clear()
        cax = horizontal_ax.imshow(heatmap,extent=extent, cmap='hot', interpolation=interpolation_method)
        fig = horizontal_ax.get_figure()

        # Plot colorbar once
        if not hasattr(horizontal_slice_plot_frame, 'check'):
            horizontal_slice_plot_frame.check = True
            fig.colorbar(cax, ax=horizontal_ax, label='Signal Sum')

        #horizontal_ax.invert_yaxis() # TODO there is some slicing ordering error
        horizontal_ax.set_aspect('auto')
        horizontal_canvas.draw()


    if data["Visualization"]["Slices"]["horizontal"] == {} and data["Visualization"]["Slices"]["vertical"] == {}:
        root.log.log_event("No Slice Data available")
    else:
        # Update Beam Plot for Seethrough Planes
        update_beam_plot(root)

    
