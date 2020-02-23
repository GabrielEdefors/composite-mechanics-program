

class Material:
    """Class that represents materials used in the laminae

               :param index: Material index
               :type index: int

     """

    def __init__(self, index, modulus, poisson_ratio, thermal_coefficient):
        self.index = index
        self.modulus = modulus
        self.poisson_ratio = poisson_ratio
        self.thermal_coefficient = thermal_coefficient
