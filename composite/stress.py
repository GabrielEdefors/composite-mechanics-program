from enum import Enum


class StressState:

    def __init__(self, components, coordinate_system: Enum, stress_type: Enum):
        self.components = components
        self.coordinate_system = coordinate_system
        self.stress_type = stress_type




