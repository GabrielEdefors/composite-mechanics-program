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
        x_labels_global = [r'$\sigma_x$' + ' [MPa]', r'$\sigma_y$' + ' [MPa]', r'$\sigma_{xy}$' + ' [MPa]']
        x_labels_local = [r'$\sigma_L$' + ' [MPa]', r'$\sigma_T$' + ' [MPa]', r'$\sigma_{LT}$' + ' [MPa]']
        axes.plot(quantity.components[component, :] / 1e6, coordinates * 1e3, colors[component])
    else:
        x_labels_global = [r'$\epsilon_x$' + ' [1e-3]', r'$\epsilon_y$' + ' [1e-3]', r'$\epsilon_{xy}$' + ' [1e-3]']
        x_labels_local = [r'$\epsilon_L$' + ' [1e-3]', r'$\epsilon_T$' + ' [1e-3]', r'$\epsilon_{LT}$' + ' [1e-3]']
        axes.plot(quantity.components[component, :] * 1e3, coordinates * 1e3, colors[component])

    axes.grid(True)

    axes.set_ylabel('z ' + "[mm]")
    if quantity.coordinate_system == CoordinateSystem.LT:
        axes.set_xlabel(x_labels_local[component])
    elif quantity.coordinate_system == CoordinateSystem.xy:
        axes.set_xlabel(x_labels_global[component])
    else:
        print("Stress type not supported")



