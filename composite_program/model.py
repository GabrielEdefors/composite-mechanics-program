from composite import read_input_file, plot_stress, FilePrint, LoadType, Laminate
from PyQt5.QtCore import *


class Model(QObject):
    """Class for the top level logic of the program
    """

    # Establish signals
    show_result = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.input_directory = ""
        self.project_name = ""
        self.project_info = dict()
        self.laminate = Laminate

    def set_input_directory(self, input_directory):
        self.input_directory = input_directory

    def set_project_name(self, name):
        self.project_name = name

    def calculate_thermal_stress(self):

        self.laminate.compute_thermal_stress()
        thermal_stresses_global, thermal_stresses_local, thermal_strains_global, thermal_strains_local, z_coordinates= \
        self.laminate.create_laminate_arrays(LoadType.thermal)

        # Plot global stresses
        axes_global = plt.subplots(nrows=1, ncols=3, constrained_layout=True, figsize=(10, 7))[1]
        fig_global = plt.figure(1)
        fig_global.suptitle('Global stresses in laminate', fontsize=16)
        plot_stress(axes=axes_global, coordinates=z_coordinates, quantity=thermal_stresses_global)

        # Plot local stresses
        axes_local = plt.subplots(nrows=1, ncols=3, constrained_layout=True, figsize=(10, 7))[1]
        fig_local = plt.figure(2)
        fig_local.suptitle('Local stresses in laminate', fontsize=16)
        plot_stress(axes=axes_local, coordinates=z_coordinates, quantity=thermal_stresses_local)

    def read_input_file(self):

        # Create a laminate instance
        self.laminate, self.project_info = read_input_file(filepath=self.input_directory)
