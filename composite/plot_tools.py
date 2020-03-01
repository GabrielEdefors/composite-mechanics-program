

def plot_stress(axes, coordinates, stress, stresstype):
    """Plot graphs of the stress components supplied by stress as a function of z coordinates

          :param axes: Axes to hold the graphs
          :type axes: list of axis objects
          :param coordinates: Element 0 an array with the z coordinates, element 1 is the unit of the values
          :type coordinates: tuple(ndarray(dtype=float, ndim=1), str)
          :param stress: Element 0 an array with the stresses, element 1 is the unit of the values
          :type stress: tuple(ndarray(dtype=float, ndim=2), str)
          :param stresstype: Either 'local' or 'global' stress
          :type stresstype: str

     """
    colors = ['blue', 'green', 'red']
    x_labels_global = [r'$\sigma_x$', r'$\sigma_y$', r'$\sigma_{xy}$']
    x_labels_local = [r'$\sigma_L$', r'$\sigma_T$', r'$\sigma_{LT}$']

    for index, axis in enumerate(axes):

        axis.plot(stress[0][index, :], coordinates[0], colors[index])
        axis.grid(True)

        axis.set_ylabel('z' + " [" + coordinates[1] + "]")
        if stresstype == 'local':
            axis.set_xlabel(x_labels_local[index] + " [" + stress[1] + "]")
        elif stresstype == 'global':
            axis.set_xlabel(x_labels_global[index] + " [" + stress[1] + "]")
        else:
            print("Stress type not supported")



