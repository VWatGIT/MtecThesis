from Python_Skripts.GUI_Panels.Panel_Updates.update_beam_plot import update_beam_plot

def update_slice_plot(root, event=None):
    tab_name = root.tab_group.select()
    tab = root.nametowidget(tab_name)

    data = tab.data 

    subtab_group = tab.nametowidget("subtab_group")
    results_frame = subtab_group.nametowidget("results_frame")
    slice_plot_frame = results_frame.nametowidget("slice_plot_frame")
    vertical_plot_frame = slice_plot_frame.nametowidget("vertical_plot_frame")

    canvas = vertical_plot_frame.canvas
    ax = canvas.figure.axes[0]

    vertical_slice_slider = slice_plot_frame.nametowidget("vertical_slice_slider")
    interpolation_checkbox = slice_plot_frame.nametowidget("interpolation_checkbox")

    interpolation_var = interpolation_checkbox.value.get()
    
    slice_index = vertical_slice_slider.get() 


    # Update the horizontal slice plot
    horizontal_plot_frame = slice_plot_frame.nametowidget("horizontal_plot_frame")
    canvas = horizontal_plot_frame.canvas
    ax = canvas.figure.axes[0]

    horizontal_slice_slider = slice_plot_frame.nametowidget("horizontal_slice_slider")
    horizontal_slice_index = horizontal_slice_slider.get()


    #only update if data is available
    if data["Visualization"]["Slices"]["vertical"] != {} :
        
        # Update the vertical slice plot
        vertical_slice= data['Visualization']["Slices"]['vertical'][str(slice_index)] # Get the slice data
        heatmap = vertical_slice['heatmap']
        keys = data['Visualization']['Slices']['vertical'].keys()
        first_key = next(iter(keys))
        extent = data['Visualization']['Slices']['vertical'][first_key]['heatmap_extent']

        # Interpolation Method with checkbox
        interpolation_method = 'nearest' if interpolation_var == 0 else 'gaussian'

        # Update the slice plot
        ax.clear()

        cax = ax.imshow(heatmap,extent=extent, cmap='hot', interpolation=interpolation_method)
        fig = ax.get_figure()

        # Plot colorbar once
        if not hasattr(vertical_plot_frame, 'check'):
            vertical_plot_frame.check = True
            fig.colorbar(cax, ax=ax, label='Signal Sum')
        
        canvas.draw()

        # Update Beam Plot for Seethrough Planes
        update_beam_plot()


    elif data["Visualization"]["Slices"]["horizontal"] != {}:

        horizontal_slice = data['Visualization']["Slices"]['horizontal'][str(horizontal_slice_index)] # Get the slice data
        heatmap = horizontal_slice['heatmap']
        extent = data['Visualization']['Slices']['horizontal'][str(horizontal_slice_index)]['heatmap_extent']

        # Update the horizontal slice plot
        ax.clear()
        cax = ax.imshow(heatmap,extent=extent, cmap='hot', interpolation=interpolation_method)
        fig = ax.get_figure()

        # Plot colorbar once
        if not hasattr(horizontal_plot_frame, 'check'):
            horizontal_plot_frame.check = True
            fig.colorbar(cax, ax=ax, label='Signal Sum')

        canvas.draw()

        # Update Beam Plot for Seethrough Planes
        update_beam_plot()

    else:
        root.log.log_event("No Slice Data available")
