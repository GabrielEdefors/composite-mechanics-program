from coordinate_systems import CoordinateSystem
from stress import StressState
from strain import StrainState


def plot_stress(axes, coordinates, quantity, component):
    """Plot graphs of the stress components supplied by stress as a function of z coordinates

          :param axes: Axes to hold the graphs
          :type axes: list of axes objects
          :param coordinates: Array with the z coordinates
          :type coordinates: ndarray(dtype=float, dim=n,1)
          :param quantity: Stress or strain state to be plotted
          :type quantity: Instance of StressState or StrainState

     """
    colors = ['blue', 'green', 'red']

    if isinstance(quantity, StressState):
        x_labels_global = [r'$\sigma_x$' + '[Pa]', r'$\sigma_y$' + '[Pa]', r'$\sigma_{xy}$' + '[Pa]']
        x_labels_local = [r'$\sigma_L$' + '[Pa]', r'$\sigma_T$' + '[Pa]', r'$\sigma_{LT}$' + '[Pa]']
    else:
        x_labels_global = [r'$\epsilon_x$' + '[-]', r'$\epsilon_y$' + '[-]', r'$\epsilon_{xy}$' + '[-]']
        x_labels_local = [r'$\epsilon_L$' + '[-]', r'$\epsilon_T$' + '[-]', r'$\epsilon_{LT}$' + '[-]']

    axes.plot(quantity.components[component, :], coordinates * 1e3, colors[component])
    axes.grid(True)

    axes.set_ylabel('z ' + "[mm]")
    if quantity.coordinate_system == CoordinateSystem.LT:
        axes.set_xlabel(x_labels_local[component])
    elif quantity.coordinate_system == CoordinateSystem.xy:
        axes.set_xlabel(x_labels_global[component])
    else:
        print("Stress type not supported")



