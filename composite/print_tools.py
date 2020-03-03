from pathlib import Path


class FilePrint:

    def __init__(self, filename):
        self.file_path = Path.cwd().joinpath('output', filename + '.txt')
        self.header = self.create_header()

    def create_header(self):
        header = "OUTPUT FILE CREATED USING COMPOSITE MECHANICS PACKAGE"
        return header

    def write_to_file(self):

        # Write header
        with open(self.file_path, mode='w') as file:

            # Header
            file.write(self.header)

