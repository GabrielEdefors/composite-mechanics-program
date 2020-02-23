import numpy as np

class Lamina:
    """Class used to represent a lamina in a laminate

               :param index: Index in lay up sequence
               :type index: int
               :param thickness: Thickness of the laminate
               :type thickness: float
               :param matrix_material: Material instance used for the matrix
               :type matrix_material: Instance of Material
               :param fibre_material: Material instance used for the fibres
               :type fibre_material: Instance of Material

     """
    # Halpin Tsai parameters
    KSI_T = 2
    KSI_G = 1

    def __init__(self, index, thickness, matrix_material, fibre_material, volume_fraction, angle):
        self.index = index
        self.thickness = thickness
        self.matrix_material = matrix_material
        self.fibre_material = fibre_material
        self.volume_fraction = volume_fraction
        self.angle = angle

        # Composite properties
        self.E_L, self.E_T, self.v_LT, self.v_TL, self.G_LT, self.alpha_L, self.alpha_T = self.composite_properties()

        # Transformation matrices
        self.T1, self.T2 = self.compute_transformation_matrices()

        # Compliance and stiffness tensors
        #self.S_global,self.S_local, self.Q_global, self.Q_local = self.compute_constitutive_matrices()

    def composite_properties(self):
        """Computes the composite properties of the lamina using the properties of the constituents.

            Theory based on rules of mixtures, Halpin Tsai and inverse rule of mixtures

         """

        # Define local variables for shorter notation
        Ef = self.fibre_material.modulus
        Em = self.matrix_material.modulus
        vf = self.fibre_material.poisson_ratio
        vm = self.matrix_material.poisson_ratio
        Vf = self.volume_fraction
        alpha_m = self.matrix_material.thermal_coefficient
        alpha_f = self.fibre_material.thermal_coefficient
        G_m = Em / 2 / (1 + vm)
        G_f = Ef / 2 / (1 + vf)

        # Inverse rule of mixtures
        E_L = Ef * Vf + Em * (1 - Vf)
        v_LT = Vf * vf + vm * (1- Vf)

        # Halpin Tsai for transverse properties
        eta_T = (Ef/Em - 1) / (Ef/Em + self.KSI_T)
        E_T = Em * (1 + self.KSI_T*eta_T*Vf) / (1 - eta_T*Vf)
        v_TL = v_LT * E_T / E_L

        # Halpin Tsai for shear properties
        eta_G = (G_f/G_m - 1) / (G_f/G_m + self.KSI_G)
        G_LT = G_m * (1 + self.KSI_G * eta_G * Vf) / (1 - eta_G * Vf)

        # Thermal expansion coefficients
        alpha_L = 1 / E_L * (alpha_f * Ef * Vf + alpha_m * Em * (1 - Vf))
        alpha_T = (1 + vf) * alpha_f * Vf + (1 + vm) * alpha_m * (1 - Vf) - alpha_L * v_LT

        return E_L, E_T, v_LT, v_TL, G_LT, alpha_L, alpha_T

    def compute_transformation_matrices(self):
        m = np.cos(np.deg2rad(self.angle))
        n = np.sin(np.deg2rad(self.angle))

        # For stress tensor
        T1 = np.array([[m**2, n**2, 2*m*n],
                      [n**2, m**2, -2*m*n],
                      [-m*n, m*n, m**2 - n**2]])

        # For strain tensor
        T2 = np.array([[m**2, n**2, m*n],
                      [n**2, m**2, -m*n],
                      [-2*m*n, 2*m*n, m**2 - n**2]])

        return T1, T2


    def compute_constitutive_matrices(self):
        a = 1









