import composite
from pathlib import Path


def replace_characters(string):
    """Clean string by replacing characters with empty string.

              :param string: string to be stripped
              :param string: string
              :returns: string_stripped
              :rtype: string
    """
    string_stripped = string.replace("\n", "")
    return string_stripped


def read_input_file(filename):
    """ Reads the input file and creates an instance of composite.Laminate which in turn holds composite.Laminae instances

                 :param filename: Input file
                 :type filename: Text file
                 :return: composite.Laminate instance, project_name
                 :rtype: Instance of composite.Laminate

       """
    filepath = Path.cwd().joinpath('input', filename)

    # Initiate empty dictionary that can store the data
    input_data = {}

    # Load input file
    with open(filepath, 'r') as file:
        for line in file:
            if line.strip() and '#' not in line:
                line = replace_characters(line)

                if line[0] == '*':
                    key = line[1:].rstrip()
                    input_data[key] = {}
                else:
                    if line[0] == '+':
                        sub_key = line[1:].rstrip()
                        input_data[key][sub_key] = []
                    else:
                        if key == 'PROJECT_INFO':
                            input_data[key][sub_key].append(line)
                        else:
                            [input_data[key][sub_key].append(float(num)) for num in line.split(',')]

    # Create instances of the materials
    materials = []
    materials_input = input_data['MATERIALS']

    for material_index, properties in materials_input.items():
        modulus = properties[0]
        poisson_ratio = properties[1]
        thermal_coefficient = properties[2]
        materials.append(composite.Material(int(material_index), modulus, poisson_ratio, thermal_coefficient))

    # Create an instance of a composite.Lamina
    lamina_data = input_data['LAMINAE']

    # Create list for storing composite.Laminae
    laminae = []
    laminae_properties = []

    for lamina_index, properties in lamina_data.items():
        thickness = properties[0]
        angle = properties[1]
        volume_fraction = properties[4]

        # Assign material instances to the laina
        for material in materials:
            if getattr(material, 'index') == int(properties[3]):
                matrix_material = material
            elif getattr(material, 'index') == int(properties[2]):
                fibre_material = material
            else:
                print('Must specify a valid material for matrix and fibres')

        # Lamina top and bottom coordinates relative bottom of bottom ply
        if int(lamina_index) == 1:
            z1 = 0
            z2 = thickness
        else:
            z1 = z2
            z2 += thickness

        laminae_properties.append((int(lamina_index), thickness, matrix_material,
                                fibre_material, volume_fraction, angle, [z1, z2]))

    for lamina_properties in laminae_properties:
        lamina_properties[6][0] -= z2/2
        lamina_properties[6][1] -= z2 / 2
        laminae.append(composite.Lamina(*lamina_properties))

    # Create an instance of composite.Laminate with the composite.Laminae
    laminate = composite.Laminate(laminae)

    # Add loads to the composite.Laminate
    loads = input_data['LOADS']
    for load_type, magnitudes in loads.items():
        if load_type == 'M':
            laminate.add_loads(moments=magnitudes)
        elif load_type == 'N':
            laminate.add_loads(normal_forces=magnitudes)
        elif load_type == 'DELTA_T':
            laminate.add_loads(delta_T=magnitudes)
        else:
            print('Unsupported load type')

    project_info = input_data['PROJECT_INFO']

    return laminate, project_info

