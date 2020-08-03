from composite import read_input_file, plot_stress, FilePrint, LoadType, Laminate
from enum import Enum
from PyQt5.QtCore import *
import numpy as np


class Model(QObject):
    """Class for the top level logic of the program
    """

    # Establish signals
    plot_data = pyqtSignal(np.ndarray, object, int)

    def __init__(self):
        super().__init__()
        self.input_directory = ""
        self.project_name = ""
        self.project_info = dict()
        self.laminate = Laminate
        self.display_coordinates = DispCoordinates.local_system

        # Laminate stress and strains
        self.thermal_stresses_global = np.ndarray([])
        self.thermal_stresses_local = np.ndarray([])
        self.thermal_strains_global = np.ndarray([])
        self.thermal_strains_local = np.ndarray([])
        self.z_coordinates = np.ndarray([])

    def set_display_coordinates(self, new_coordinates: Enum):
        self.display_coordinates = new_coordinates

    def set_input_directory(self, input_directory):
        self.input_directory = input_directory

    def set_project_name(self, name):
        self.project_name = name

    def calculate_thermal_stress(self):

        self.laminate.compute_thermal_stress()
        self.thermal_stresses_global, self.thermal_stresses_local, self.thermal_strains_global, \
        self.thermal_strains_local, self.z_coordinates = self.laminate.create_laminate_arrays(LoadType.thermal)

        # Plot the local thermal stress component 0 as default
        self.plot_data.emit(self.z_coordinates, self.thermal_stresses_local, 0)

    def change_plot_component(self, quantity: Enum, component: int):

        # Redraw canvas with new component
        if self.display_coordinates == DispCoordinates.local_system:
            if quantity == Quantity.stress:
                self.plot_data.emit(self.z_coordinates, self.thermal_stresses_local, component)
            elif quantity == Quantity.strain:
                self.plot_data.emit(self.z_coordinates, self.thermal_strains_local, component)

        elif self.display_coordinates == DispCoordinates.global_system:
            if quantity == Quantity.stress:
                self.plot_data.emit(self.z_coordinates, self.thermal_stresses_global, component)
            elif quantity == Quantity.strain:
                self.plot_data.emit(self.z_coordinates, self.thermal_strains_global, component)

    def read_input_file(self):

        # Create a laminate instance
        self.laminate, self.project_info = read_input_file(filepath=self.input_directory)


class DispCoordinates(Enum):
    local_system = 1
    global_system = 2


class Quantity(Enum):
    stress = 1
    strain = 2