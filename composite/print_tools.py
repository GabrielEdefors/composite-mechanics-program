from pathlib import Path
from csv import writer, DictWriter


class FilePrint:

    def __init__(self, filename):
        self.file_path = Path.cwd().joinpath('output', filename + '.csv')
        self.project_info = ['**DATE: 040320', '**TIME: 15:24:44', '**AUTHORS: Gabriel Edefors']
        self.header = ['OUTPUT FILE CREATED USING COMPOSITE MECHANICS PACKAGE']
        self.create_header()

    def create_header(self):

        with open(self.file_path, 'w', newline='\n') as csvfile:
            csv_writer = writer(csvfile)
            csv_writer.writerow(self.header)
            csv_writer.writerow(['.'])
            csv_writer.writerow(['='*42 + '   PROJECT INFO   ' + '='*42])
            csv_writer.writerow(['.'])
            for line in self.project_info:
                csv_writer.writerow([line])
            csv_writer.writerow(['.'])
            csv_writer.writerow(['=' * 101])
            csv_writer.writerow(['.'])

    def write_to_file(self, data):
        field_names = ['index', 'max_thermal_stress', 'min_thermal_stress']

        with open(self.file_path, 'a+', newline='\n') as csvfile:
            csv_writer = writer(csvfile)
            csv_writer.writerow(['.'])
            csv_writer.writerow(['='*38 + '   THERMAL STRESS DATA   ' + '='*38])
            csv_writer.writerow(['.'])

        # Write header
        with open(self.file_path, 'a+', newline='') as csvfile:

            dict_writer = DictWriter(csvfile, fieldnames=field_names)

            dict_writer.writeheader()
            dict_writer.writerows(data)
