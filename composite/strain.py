from enum import Enum


class StrainState:

    def __init__(self, components, coordinate_system: Enum, strain_type: Enum):
        self.components = components
        self.coordinate_system = coordinate_system
        self.strain_type = strain_type