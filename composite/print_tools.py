from pathlib import Path
from csv import writer, DictWriter
import math


class FilePrint:

    def __init__(self, info, filename):
        self.file_path = Path.cwd().joinpath('output', filename + '.txt')
        self.page_width = 90
        self.info = info

        # Read and write package info
        header = open(Path.cwd().joinpath('input', 'header.txt'), "r")
        file = open(self.file_path, "w")
        file.write(header.read())
        file.close()

    def print_project_info(self):

        with open(self.file_path, 'a', newline='\n') as file:

            self.print_section(list(self.info.keys())[0], file)

            for key, value in self.info['PROJECT_INFO'].items():
                file.write('** ' + key + ': ' + value[0] + '\n')

            file.write('.' + '\n')

    def print_section(self, section, file):
        margin = 4
        line_len1 = math.ceil((self.page_width - len(section)) / 2) - margin
        line_len2 = self.page_width - line_len1 - len(section) - margin * 2
        file.write('.' + '\n')
        file.write('=' * line_len1 + ' ' * margin + section + ' ' * margin + line_len2 * '=' + '\n')
        file.write('.' + '\n')

    def print_data(self, data, field_names=['index', 'max_thermal_stress', 'min_thermal_stress']):

        with open(self.file_path, 'a+') as file:
            print(data, file=file)
            # csv_dictwriter = DictWriter(csvfile, field_names)
            # csv_writer = writer()
            #
            # csv_writer.writerow(['.'])
            # csv_dictwriter.writeheader()
            #
            # for row in data:
            #     csv_dictwriter.writerow(row)


