from coordinate_systems import CoordinateSystem

def plot_stress(axes, coordinates, stress):
    """Plot graphs of the stress components supplied by stress as a function of z coordinates

          :param axes: Axes to hold the graphs
          :type axes: list of axis objects
          :param coordinates: Array with the z coordinates
          :type coordinates: ndarray(dtype=float, dim=n,1)
          :param stress: Stress or strain state to be plotted
          :type stress: Instance of StressState or StrainState

     """
    colors = ['blue', 'green', 'red']
    x_labels_global = [r'$\sigma_x$', r'$\sigma_y$', r'$\sigma_{xy}$']
    x_labels_local = [r'$\sigma_L$', r'$\sigma_T$', r'$\sigma_{LT}$']

    for index, axis in enumerate(axes):

        axis.plot(stress.components[index, :], coordinates, colors[index])
        axis.grid(True)

        axis.set_ylabel('z' + "[m]")
        if stress.coordinate_system == CoordinateSystem.LT:
            axis.set_xlabel(x_labels_local[index] + " [Pa]")
        elif stress.coordinate_system == CoordinateSystem.xy:
            axis.set_xlabel(x_labels_global[index] + " [Pa]")
        else:
            print("Stress type not supported")



