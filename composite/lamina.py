

class Lamina:
    """Class used to represent a lamina in a laminate

               :param index: Index in lay up sequence
               :type index: int
               :param thickness: Thickness of the laminate
               :type thickness: float
               :param matrix_material: Material instance used for the matrix
               :type thickness: Instance of Material
               :param fibre_material: Material instance used for the fibres
               :type thickness: Instance of Material

     """

    def __init__(self, index, thickness, matrix_material, fibre_material, volume_fraction, angle):
        self.index = index
        self.thickness = thickness
        self.matrix_material = matrix_material
        self.fibre_material = fibre_material
        self.volume_fraction = volume_fraction
        self.angle = angle

        # Composite properties
        self.E_L, self.v_LT = self.composite_properties()


        self.E_T = 0
        self.G_LT = 0
        self.alpha_L = 0
        self.alpha_T = 0

    def composite_properties(self):

        E_L = self.fibre_material.modulus * self.volume_fraction\
                   + self.matrix_material.modulus * (1 - self.volume_fraction)

        v_LT = self.volume_fraction * self.matrix_material.poisson_ratio\
                    + self.fibre_material.poisson_ratio * (1 - self.volume_fraction)

        return E_L, v_LT







