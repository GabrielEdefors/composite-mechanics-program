from composite import read_input_file, plot_stress, FilePrint, LoadType, Laminate
from coordinate_systems import CoordinateSystem
from enum import Enum
from PyQt5.QtCore import *
import numpy as np

class Quantity(Enum):
    stress = 1
    strain = 2


class ResultData:

    def __init__(self, stresses_global, stresses_local, strains_global,
                 strains_local, z_coordinates):

        # Data that should be displayed
        self.global_stress = stresses_global
        self.local_stress = stresses_local
        self.global_strains = strains_global
        self.local_strains = strains_local
        self.z_coordinates = z_coordinates


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

        # Object to store the different data
        self.result_thermal = ResultData
        self.result_total = ResultData

        # Attributes that keeps track of what is currently displayed in canvas
        self.display_category = self.result_thermal
        self.display_quantity = Quantity
        self.display_component = int
        self.display_coordinates = CoordinateSystem.LT
        self.z_coordinates = np.ndarray

    def set_display_coordinates(self, new_coordinates: CoordinateSystem):
        self.result.display_coordinates = new_coordinates

    def set_display_category(self, category: ResultData):
        self.display_category = category

    def set_input_directory(self, input_directory):
        self.input_directory = input_directory

    def set_project_name(self, name):
        self.project_name = name

    def calculate_thermal_stress(self):

        self.laminate.compute_thermal_stress()
        thermal_stresses_global, thermal_stresses_local, thermal_strains_global, \
            thermal_strains_local, z_coordinates = self.laminate.create_laminate_arrays(LoadType.thermal)
        self.z_coordinates = z_coordinates

        # Create result object for thermal loads
        self.result_thermal = ResultData(thermal_stresses_global, thermal_stresses_local, thermal_strains_global, \
            thermal_strains_local, z_coordinates)

        # Plot the local thermal stress component 0 in local coordinates as default
        self.set_plot_component(0)
        self.set_display_coordinates(CoordinateSystem.LT)
        self.set_plot_quantity(Quantity.stress)
        self.display_category = self.result_thermal
        self.plot_display_data.emit()

    def set_plot_component(self, component: int):
        self.display_component = component

    def set_plot_quantity(self, quantity: Quantity):
        self.display_category = quantity

    def change_display_coordinates(self, coordinates: CoordinateSystem):
        self.display_coordinates = coordinates

    def read_input_file(self):

        # Create a laminate instance
        self.laminate, self.project_info = read_input_file(filepath=self.input_directory)


