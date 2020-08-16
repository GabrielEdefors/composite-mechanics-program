from coordinate_systems import CoordinateSystem
from stress import StressState
from strain import StrainState

def plot_stress(axes, coordinates, quantity):
    """Plot graphs of the stress components supplied by stress as a function of z coordinates

          :param axes: Axes to hold the graphs
          :type axes: list of axis objects
          :param coordinates: Array with the z coordinates
          :type coordinates: ndarray(dtype=float, dim=n,1)
          :param quantity: Stress or strain state to be plotted
          :type quantity: Instance of StressState or StrainState

     """
    colors = ['blue', 'green', 'red']

    if isinstance(quantity, StressState):
        x_labels_global = [r'$\sigma_x$', r'$\sigma_y$', r'$\sigma_{xy}$']
        x_labels_local = [r'$\sigma_L$', r'$\sigma_T$', r'$\sigma_{LT}$']
    else:
        x_labels_global = [r'$\epsilon_x$', r'$\epsilon_y$', r'$\epsilon_{xy}$']
        x_labels_local = [r'$\epsilon_L$', r'$\epsilon_T$', r'$\epsilon_{LT}$']

    for index, axis in enumerate(axes):

        axis.plot(quantity.components[index, :], coordinates, colors[index])
        axis.grid(True)

        axis.set_ylabel('z' + "[m]")
        if quantity.coordinate_system == CoordinateSystem.LT:
            axis.set_xlabel(x_labels_local[index] + " [Pa]")
        elif quantity.coordinate_system == CoordinateSystem.xy:
            axis.set_xlabel(x_labels_global[index] + " [Pa]")
        else:
            print("Stress type not supported")




