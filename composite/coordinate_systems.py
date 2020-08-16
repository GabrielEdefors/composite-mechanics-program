from enum import Enum


class CoordinateSystem(Enum):
    xy = 1
    LT = 2

    def __str__(self):
        if self.name == 'xy':
            string = 'Local Coordinates'
        else:
            string = 'Global Coordinates'
        return string
