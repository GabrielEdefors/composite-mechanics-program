from composite import read_input_file, plot_stress, FilePrint, LoadType, Laminate, Quantity
from coordinate_systems import CoordinateSystem
from enum import Enum
from PyQt5.QtCore import *
import numpy as np


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
    plot_display_data = pyqtSignal()

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
        self.display_load_type = self.result_thermal
        self.display_quantity = Quantity
        self.display_component = int
        self.display_coordinates = CoordinateSystem.LT
        self.z_coordinates = np.ndarray

    def set_display_loadtype(self, load_type: LoadType):

        if load_type == LoadType.thermal:
            self.display_load_type = self.result_thermal
        else:
            self.display_load_type = self.result_total

    def set_display_coordinates(self, new_coordinates: CoordinateSystem):
        self.display_coordinates = new_coordinates

    def set_display_category(self, load_type: ResultData):
        self.display_load_type = load_type

    def set_input_directory(self, input_directory):
        self.input_directory = input_directory

    def set_project_name(self, name):
        self.project_name = name
        self.project_info['NAME'] = [name]

    def calculate(self, thermal_stress, total_stress):

        if thermal_stress is True:
            self.calculate_thermal_stress()
        if total_stress is True:
            self.calculate_total_stress()

    def calculate_thermal_stress(self):

        self.laminate.compute_thermal_stress()
        thermal_stresses_global, thermal_stresses_local, thermal_strains_global, \
            thermal_strains_local, z_coordinates = self.laminate.create_laminate_arrays(LoadType.thermal)
        self.z_coordinates = z_coordinates

        # Create result object for thermal loads
        self.result_thermal = ResultData(thermal_stresses_global, thermal_stresses_local, thermal_strains_global, \
            thermal_strains_local, z_coordinates)

        # Plot the local thermal stress component 0 in local coordinates as default
        self.set_display_component(0)
        self.set_display_coordinates(CoordinateSystem.LT)
        self.set_display_quantity(Quantity.stress)
        self.display_load_type = self.result_thermal
        self.plot_display_data.emit()

    def calculate_total_stress(self):

        self.laminate.compute_total_stress()
        total_stresses_global, total_stresses_local, total_strains_global, \
            total_strains_local, z_coordinates = self.laminate.create_laminate_arrays(LoadType.combined)
        self.z_coordinates = z_coordinates

        # Create result object for thermal loads
        self.result_total = ResultData(total_stresses_global, total_stresses_local, total_strains_global, \
                            total_strains_local, z_coordinates)

        # Plot the local total stress component 0 in local coordinates as default
        self.set_display_component(0)
        self.set_display_coordinates(CoordinateSystem.LT)
        self.set_display_quantity(Quantity.stress)
        self.display_load_type = self.result_total
        self.plot_display_data.emit()

    def set_display_component(self, component: int):
        self.display_component = component

    def set_display_quantity(self, quantity: Quantity):
        self.display_quantity = quantity

    def change_display_coordinates(self, coordinates: CoordinateSystem):
        self.display_coordinates = coordinates

    def read_input_file(self):

        # Create a laminate instance
        self.laminate, self.project_info = read_input_file(filepath=self.input_directory)

    def export_text_file(self, filepath, ):

        print_obj = FilePrint({'PROJECT_INFO': self.project_info}, filepath=filepath)
        print_obj.print_project_info()
        print_obj.print_output_data(self.laminate, load_type=LoadType.thermal)
        print_obj.print_output_data(self.laminate, load_type=LoadType.combined)



