from pathlib import Path
from composite import Lamina, Laminate, read_input_file

# Read input file
filename = 'assignment_1.txt'
filepath = Path.cwd().joinpath('input', filename)

laminate = read_input_file(filepath)

print(laminate.laminae[0].v_LT)











