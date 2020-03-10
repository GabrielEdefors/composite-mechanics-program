from pathlib import Path
from composite import LoadType
from enum import Enum
import time
import math


class FilePrint:
    """Manages parameters and methods for writing results to a text file

          :param info: Project info to include in the file
          :type info: Dict
          :param filename: Name of the file excluding file type
          :type filename: string

     """

    def __init__(self, info, filename):
        self.file_path = Path.cwd().joinpath('output', filename + '.txt')
        self.info = info
        self.column_width = 18
        self.page_width = self.column_width * 6

        # Read and write package info
        header = open(Path.cwd().joinpath('input', 'header.txt'), "r")
        file = open(self.file_path, "w")
        file.write(header.read())

        # Write current time
        file.write('\n')
        localtime = time.asctime(time.localtime(time.time()))
        file.write('Results computed at: ' + str(localtime) + '\n')

        file.close()

    def print_project_info(self):
        """Prints the info specified in the info parameter"""

        with open(self.file_path, 'a', newline='\n') as file:

            self.print_title(list(self.info.keys())[0], file)

            for key, value in self.info['PROJECT_INFO'].items():
                file.write('** ' + key + ': ' + value[0] + '\n')

    def print_title(self, title_name, file):
        """Prints the title specified in title_name

              :param title_name: Title to print
              :type title_name: str
              :param file: File to write to
              :type file: writable file obj

        """

        margin = 4
        line_len1 = math.ceil((self.page_width - len(title_name)) / 2) - margin
        line_len2 = self.page_width - line_len1 - len(title_name) - margin * 2
        file.write('.' + '\n')
        file.write('=' * line_len1 + ' ' * margin + title_name + ' ' * margin + line_len2 * '=' + '\n')
        file.write('.' + '\n')

    def print_output_data(self, laminate, load_type: Enum):
        """Prints the output data specified by type

              :param laminate: Laminate to retrieve data from
              :type laminate: Instance of Laminate
              :param load_type: Stress or strain type, either total or thermal
              :type load_type: str

        """

        with open(self.file_path, 'a', newline='\n') as file:

            header_global = ['INDEX', 'ANGLE', 'Z-COORDINATE', 'STRESS_X', 'STRESS_Y', 'STRESS_XY']
            header_local = ['INDEX', 'ANGLE', 'Z-COORDINATE', 'STRESS_L', 'STRESS_T', 'STRESS_LT']

            # Print section
            if load_type == LoadType.total:
                self.print_title('TOTAL STRESS DATA', file)
            else:
                self.print_title('THERMAL STRESS DATA', file)

            # print global stress header
            file.write(self.format_columns(header_global, data_type='header'))

            # Print global stress
            for lamina in laminate.laminae:
                for i in range(2):
                    if load_type == LoadType.total:
                        stress_data = lamina.global_properties.total_stress
                    else:
                        stress_data = lamina.global_properties.thermal_stress
                    self.print_lamina_data(lamina, stress_data, i, file)

            file.write('.\n')

            # print local stress header
            file.write(self.format_columns(header_local, data_type='header'))

            # Print local stress
            for lamina in laminate.laminae:
                for i in range(2):
                    if load_type == LoadType.total:
                        stress_data = lamina.local_properties.total_stress
                    else:
                        stress_data = lamina.local_properties.thermal_stress
                    self.print_lamina_data(lamina, stress_data, i, file)

    def print_lamina_data(self, lamina, stress, i, file):
        """Prints lamina index, coordinate, stress components

              :param lamina: Lamina to retrieve data from
              :type lamina: Instance of Lamina
              :param stress: Stress to print
              :type stress: ndarray(dtype=float, dim=3,2)
              :param i: 0 for bottom of ply and 1 for top
              :type i: int
              :param file: File to write to
              :type file: writable file obj

        """
        z = lamina.coordinates[i]
        angle = lamina.angle
        sigma_1 = stress.components[0, i]
        sigma_2 = stress.components[1, i]
        sigma_3 = stress.components[2, i]
        data = [lamina.index, angle, z, sigma_1, sigma_2, sigma_3]

        file.write(self.format_columns(data, data_type='stress/strain'))

    def format_columns(self, data, data_type='stress/strain'):
        """Formats the column data specified in data_type

            :param data: Data to print
            :type data: List(len=6)
            :param data_type: Either stress/strain or header, determines the formatting
            :type data_type: str
            :returns: Formatted string ready to print
            :rtype: str
        """

        if data_type == 'stress/strain':
            data_string = f'{data[0]:>{self.column_width}}{data[1]:>{self.column_width}}' \
                              f'{data[2]:>{self.column_width}.4e}{data[3]:>{self.column_width}.4e}' \
                              f'{data[4]:>{self.column_width}.4e}{data[5]:>{self.column_width}.4e}' + '\n'

        else:
            data_string = f'{data[0]:>{self.column_width}}{data[1]:>{self.column_width}}' \
                              f'{data[2]:>{self.column_width}}{data[3]:>{self.column_width}}' \
                              f'{data[4]:>{self.column_width}}{data[5]:>{self.column_width}}' + '\n'

        return data_string













