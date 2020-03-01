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

               :ivar E_L: Longitudinal Stiffness of lamina
               :ivar E_T: Transverse stiffness of lamina
               :ivar v_LT: Poisson ratio relative longitudinal loading
               :ivar G_LT: Shear stiffness of lamina
               :ivar alpha_L: Thermal coefficient in transverse direction
               :ivar alpha_T: Thermal coefficient in longitudinal direction
               :ivar local_properties: Instance of LocalLaminaProperties
               :ivar global_properties: Instance of GlobalLaminaProperties
               :ivar T1: Transformation matrix for stress
               :ivar T2: Transformation matrix for strain
     """

    # Halpin Tsai parameters
    KSI_T = 2
    KSI_G = 1

    def __init__(self, index, thickness, matrix_material, fibre_material, volume_fraction, angle, coordinates):
        self.index = index
        self.thickness = thickness
        self.matrix_material = matrix_material
        self.fibre_material = fibre_material
        self.volume_fraction = volume_fraction
        self.angle = angle
        self.coordinates = coordinates

        # Homogenised properties
        self.E_L, self.E_T, self.v_LT, self.v_TL, self.G_LT, self.alpha_L, self.alpha_T = self.compute_composite_properties()

        # Transformation matrices
        self.T1, self.T2 = self.compute_transformation_matrices()

        # Create one instance with local properties and one with global properties
        self.local_properties = LocalLaminaProperties(self)
        self.global_properties = GlobalLaminaProperties(self)

        # Create an instance with the stress state of the lamina
        self.stress = StressState(self)

    def compute_composite_properties(self):
        """Computes the composite properties of the lamina using the properties of the constituents.

            Theory based on rules of mixtures, Halpin Tsai and inverse rule of mixtures

              :returns: E_L, E_T, v_LT, v_TL, G_LT, alpha_L, alpha_T
              :rtype: Tuple of floats
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
        """Computes the coordinate transformation matrices for stress and strain tensors

              :returns: T_1(ndarray(dtype=float, ndim=2)), T_2(ndarray(dtype=float, ndim=2))
         """

        m = np.cos(np.deg2rad(self.angle))
        n = np.sin(np.deg2rad(self.angle))

        # For stress matrix
        T1 = np.array([[m**2, n**2, 2*m*n],
                      [n**2, m**2, -2*m*n],
                      [-m*n, m*n, m**2 - n**2]])

        # For strain matrix
        T2 = np.array([[m**2, n**2, m*n],
                      [n**2, m**2, -m*n],
                      [-2*m*n, 2*m*n, m**2 - n**2]])

        return T1, T2


class LocalLaminaProperties:
    """Class used to represent the local properties of a lamina

                   :param lamina: Parent lamina
                   :type lamina: Instance of Lamina
                   :ivar S: Compliance matrix
                   :ivar Q: Stiffness matrix
    """

    def __init__(self, lamina):
        self.lamina = lamina
        self.S, self.Q = self.compute_constitutive_matrices()

    def compute_constitutive_matrices(self):
        """Computes the compliance and stiffness tensors in local coordinate system

              :returns: Q(ndarray(dtype=float, ndim=2)), S(ndarray(dtype=float, ndim=2)),
         """

        # Compliance matrix
        S = np.array([[1 / self.lamina.E_L, -self.lamina.v_LT / self.lamina.E_L, 0],
                            [-self.lamina.v_LT / self.lamina.E_L, 1 / self.lamina.E_T, 0],
                            [0, 0, 1 / self.lamina.G_LT]], )

        # Stiffness matrix
        Q = np.linalg.inv(S)

        return S, Q


class GlobalLaminaProperties:
    """Class used to represent the global properties of a lamina

                   :param lamina: Parent lamina
                   :type lamina: Instance of Lamina
                   :ivar S: Compliance matrix
    """

    def __init__(self, lamina):
        self.lamina = lamina
        self.S, self.Q = self.compute_constitutive_matrices()

        # Thermal coefficients
        alpha_local = np.array([self.lamina.alpha_L, self.lamina.alpha_T, 0]).reshape(3, 1)
        self.alpha = np.linalg.inv(self.lamina.T2).dot(alpha_local)

        # Contributions to extension, bending and coupling matrix
        self.Ak = self.Q.dot(self.lamina.coordinates[1] - self.lamina.coordinates[0])
        self.Bk = 1 / 2 * self.Q.dot(self.lamina.coordinates[1] ** 2 - self.lamina.coordinates[0] ** 2)
        self.Dk = 1 / 3 * self.Q.dot(self.lamina.coordinates[1] ** 3 - self.lamina.coordinates[0] ** 3)

    def compute_constitutive_matrices(self):
        """Computes the compliance and stiffness tensors in local coordinate system

              :returns: Q(ndarray(dtype=float, ndim=2)), S(ndarray(dtype=float, ndim=2)),
         """

        # Compliance matrix
        S = np.linalg.multi_dot([np.linalg.inv(self.lamina.T1), self.lamina.local_properties.S, self.lamina.T2])

        # Stiffness matrix
        Q = np.linalg.multi_dot([np.linalg.inv(self.lamina.T1), self.lamina.local_properties.Q, self.lamina.T2])

        return S, Q


class StressState:
    """Class used to represent the stress state of a lamina

                       :param lamina: Parent lamina
                       :type lamina: Instance of Lamina
                       :ivar mechanical_strains_global: Array containing strain components in order x, y, xy
                       :ivar mechanical_stress_global: Array containing stress components in order x, y, xy
                       :ivar mechanical_strains_local: Array containing strain components in order x, y, xy
                       :ivar mechanical_stress_local: Array containing stress components in order x, y, xy
        """

    def __init__(self, lamina):
        self.lamina = lamina
        self.mechanical_strains_global = np.zeros((3, 2))
        self.mechanical_stress_global = np.zeros((3, 2))
        self.mechanical_strains_local = np.zeros((3, 2))
        self.mechanical_stress_local = np.zeros((3, 2))

    def compute_mechanical_strains(self, midplane_strains, curvatures, delta_T):
        """Computes the mechanical strains caused by change in temperature delta_T

              :param midplane_strains: Contains strain components in order x, y, xy
              :type midplane_strains: ndarray(dtype=float, ndim=1)
              :param curvatures: Contains curvature components in order x, y, xy
              :type curvatures: ndarray(dtype=float, ndim=1)
              :param delta_T: Temperature difference
              :type delta_T: float

         """

        self.mechanical_strains_global[:, 0, np.newaxis] = midplane_strains + self.lamina.coordinates[0] * curvatures -\
                                                           self.lamina.global_properties.alpha * delta_T

        self.mechanical_strains_global[:, 1, np.newaxis] = midplane_strains + self.lamina.coordinates[1] * curvatures -\
                                                           self.lamina.global_properties.alpha * delta_T

    def compute_mechanical_stress(self):
        """Computes the mechanical stress caused by change in temperature delta_T

              :returns: mechanical_stress_global(ndarray(dtype=float, ndim=1)),
                        mechanical_strains_global(ndarray(dtype=float, ndim=1))

         """

        # Calculate stresses corresponding to strains
        self.mechanical_stress_global[:, 0, np.newaxis] = \
            self.lamina.global_properties.Q.dot(self.mechanical_strains_global[:, 0, np.newaxis])

        self.mechanical_stress_global[:, 1, np.newaxis] = \
            self.lamina.global_properties.Q.dot(self.mechanical_strains_global[:, 1, np.newaxis])

        self.mechanical_stress_local[:, 0, np.newaxis] = \
            self.lamina.T1.dot(self.mechanical_stress_global[:, 0, np.newaxis])

        self.mechanical_stress_local[:, 1, np.newaxis] = \
            self.lamina.T1.dot(self.mechanical_stress_global[:, 1, np.newaxis])

        return self.mechanical_stress_global, self.mechanical_stress_local

