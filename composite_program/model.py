import numpy as np
from PyQt5.QtCore import *

from composite import read_input_file, FilePrint, LoadType, Laminate, Quantity, ExcelPrint
from coordinate_systems import CoordinateSystem


class ResultData:
    """Class for storing the computed results

        :param: stresses_global: Global stresses in the laminate
        :type stresses_global: ndarray(dtype=float, dim=3,nr_laminae*2)
        :param: stresses_local: Local stresses in the laminate
        :type stresses_local: ndarray(dtype=float, dim=3,nr_laminae*2)
        :param: strains_global: Global strains in the laminate
        :type strains_global: ndarray(dtype=float, dim=3,nr_laminae*2)
        :param: strains_local: Local strains in the laminate
        :type strains_local: ndarray(dtype=float, dim=3,nr_laminae*2)
        :param: z_coordinates: Z coordinates (two at each interface) at each interface of the laminate
        :type z_coordinates: ndarray(dtype=float, dim=1,nr_laminae*2)


    """

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

    # Establish signals to the view
    plot_display_data = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.input_directory = ""
        self.project_name = ""
        self.project_info = dict()
        self.laminate = Laminate

        # Objects to store the computed data
        self.result_thermal = ResultData
        self.result_total = ResultData

        # Attributes that keeps track of what is currently displayed on the canvas canvas
        self.display_load_type = self.result_thermal
        self.display_quantity = Quantity
        self.display_component = int
        self.display_coordinates = CoordinateSystem.LT
        self.z_coordinates = np.ndarray

    def set_display_loadtype(self, load_type: LoadType):
        """Sets the currently displayed load type

            :param load_type: Load type that should be displayed
            :type load_type: LoadType Enum

        """

        if load_type == LoadType.thermal:
            self.display_load_type = self.result_thermal
        else:
            self.display_load_type = self.result_total

    def set_display_coordinates(self, new_coordinates: CoordinateSystem):
        """Sets the currently displayed coordinates

            :param new_coordinates: Load type that should be displayed
            :type load_type: LoadType Enum

        """
        self.display_coordinates = new_coordinates

    def set_display_category(self, load_category: ResultData):
        """Sets the currently displayed category

            :param new_coordinates: Category that should be displayed
            :type load_category: ResultData

        """
        self.display_load_type = load_category

    def set_display_component(self, component: int):
        """Sets the currently displayed component

            :param component: Component that should be displayed
            :type component: int

        """
        self.display_component = component

    def set_display_quantity(self, quantity: Quantity):
        """Sets the currently displayed quantity

            :param quantity: quantity that should be displayed
            :type quantity: int

        """
        self.display_quantity = quantity

    def set_input_directory(self, input_directory):
        self.input_directory = input_directory

    def set_project_name(self, name):
        self.project_name = name
        self.project_info['NAME'] = [name]

    def calculate(self, thermal_stress, total_stress):
        """Redirects the signal to calculate to either thermal or total stress methods"""
        if thermal_stress is True:
            self.calculate_thermal_stress()
        if total_stress is True:
            self.calculate_total_stress()

    def calculate_thermal_stress(self):
        """Calculates the thermal stress and stores the results in results_thermal"""

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
        """Calculates the total stress and stores the results in results_thermal"""

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

    def change_display_coordinates(self, coordinates: CoordinateSystem):
        self.display_coordinates = coordinates

    def read_input_file(self):
        """Reads the input file and create a laminate instance"""

        # Create a laminate instance
        self.laminate, self.project_info = read_input_file(filepath=self.input_directory)

    def export_text_file(self, filepath, include_thermal=False, include_total=False):
        """Prints the result specified to a text file

            :param filepath: Filepath of the text file
            :type filepath: str
            :param include_thermal: True if should be included, False otherwise
            :param include_total: True if should be included, False otherwise

        """

        print_obj = FilePrint({'PROJECT_INFO': self.project_info}, filepath=filepath)
        print_obj.print_project_info()

        if include_thermal:
            print_obj.print_output_data(self.laminate, load_type=LoadType.thermal)
        if include_total:
            print_obj.print_output_data(self.laminate, load_type=LoadType.combined)

    def export_Excel_file(self, filepath, include_thermal=False, include_total=False):
        """Prints the result specified to an Excel workbook

            :param filepath: Filepath of the text file
            :type filepath: str
            :param include_thermal: True if should be included, False otherwise
            :param include_total: True if should be included, False otherwise

        """

        print_object = ExcelPrint({'PROJECT_INFO': self.project_info}, filepath)

        if include_thermal:
            print_object.write_data(self.laminate, load_type=LoadType.thermal)
        if include_total:
            print_object.write_data(self.laminate, load_type=LoadType.combined)
