import numpy as np
from enum import Enum
from strain import StrainState
from stress import StressState
from coordinate_systems import CoordinateSystem
from laminate import LoadType

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
        self.angle = angle
        self.thickness = thickness
        self.coordinates = coordinates
        self.matrix_material = matrix_material
        self.fibre_material = fibre_material
        self.volume_fraction = volume_fraction

        # Homogenised properties
        self.E_L, self.E_T, self.v_LT, self.v_TL, self.G_LT, self.alpha_L, self.alpha_T = self.compute_composite_properties()

        # Transformation matrices
        self.T1, self.T2 = self.compute_transformation_matrices()

        # Create one instance with local properties and one with global properties
        self.local_properties = LocalLaminaProperties(self)
        self.global_properties = GlobalLaminaProperties(self)

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

              :returns: T_1, T_2
              :rtype: ndarray(dtype=float, dim=3,3)

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
                   :ivar S: Compliance matrix ndarray(dtype=float, dim=3,3)
                   :ivar Q: Stiffness matrix ndarray(dtype=float, dim=3,3)
    """

    def __init__(self, lamina):
        self.lamina = lamina
        self.coordinate_system = CoordinateSystem.LT
        self.S, self.Q = self.compute_constitutive_matrices()

        # Strain state
        self.thermal_strain = StrainState(np.zeros((3, 2)), self.coordinate_system, LoadType.thermal)
        self.total_strain = StrainState(np.zeros((3, 2)), self.coordinate_system, LoadType.thermal)

        # Stress state
        self.thermal_stress = StressState(np.zeros((3, 2)), self.coordinate_system, LoadType.thermal)
        self.total_stress = StressState(np.zeros((3, 2)), self.coordinate_system, LoadType.thermal)

    def compute_thermal_strains(self):
        local_components = self.lamina.T2.dot(self.lamina.global_properties.thermal_strain.components)
        self.thermal_strain.components = local_components

    def compute_total_strains(self):
        local_components = self.lamina.T2.dot(self.lamina.global_properties.total_strain.components)
        self.total_strain.components = local_components

    def compute_thermal_stress(self):
        local_components = self.lamina.T1.dot(self.lamina.global_properties.thermal_stress.components)
        self.thermal_stress.components = local_components

    def compute_total_stress(self):
        local_components = self.lamina.T1.dot(self.lamina.global_properties.total_stress.components)
        self.total_stress.components = local_components
        print(self.total_stress.components)
        print(self.lamina.global_properties.total_stress.components)

    def compute_constitutive_matrices(self):
        """Computes the compliance and stiffness tensors in local coordinate system

              :returns: Q, S
              :rtype: ndarray(dtype=float, dim=3,3)
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
                   :ivar S: Compliance matrix ndarray(dtype=float, dim=3,3)
                   :ivar Q Stiffness matrix ndarray(dtype=float, dim=3,3)

    """

    def __init__(self, lamina):
        self.lamina = lamina
        self.coordinate_system = CoordinateSystem.xy
        self.S, self.Q = self.compute_constitutive_matrices()

        # Strain state
        self.thermal_strain = StrainState(np.zeros((3, 2)), self.coordinate_system, LoadType.thermal)
        self.total_strain = StrainState(np.zeros((3, 2)), self.coordinate_system, LoadType.thermal)

        # Stress state
        self.thermal_stress = StressState(np.zeros((3, 2)), self.coordinate_system, LoadType.thermal)
        self.total_stress = StressState(np.zeros((3, 2)), self.coordinate_system, LoadType.thermal)

        # Thermal coefficients
        alpha_local = np.array([lamina.alpha_L, lamina.alpha_T, 0]).reshape(3, 1)
        self.alpha = np.linalg.inv(lamina.T2).dot(alpha_local)

        # Contributions to extension, bending and coupling matrix
        self.Ak = self.Q.dot(lamina.coordinates[1] - lamina.coordinates[0])
        self.Bk = 1 / 2 * self.Q.dot(lamina.coordinates[1] ** 2 - lamina.coordinates[0] ** 2)
        self.Dk = 1 / 3 * self.Q.dot(lamina.coordinates[1] ** 3 - lamina.coordinates[0] ** 3)

    def compute_constitutive_matrices(self):
        """Computes the compliance and stiffness tensors in local coordinate system

              :returns: Q, S
              :rtype: ndarray(dtype=float, dim=3,3)

         """

        # Compliance matrix
        S = np.linalg.multi_dot([np.linalg.inv(self.lamina.T1), self.lamina.local_properties.S, self.lamina.T2])

        # Stiffness matrix
        Q = np.linalg.multi_dot([np.linalg.inv(self.lamina.T1), self.lamina.local_properties.Q, self.lamina.T2])

        return S, Q

    def compute_mechanical_strains(self, midplane_strains, curvatures, *delta_T):
        """Computes the mechanical strains caused by change in temperature delta_T

              :param midplane_strains: Contains strain components in order x, y, xy
              :type midplane_strains: ndarray(dtype=float, dim=3,1)
              :param curvatures: Contains curvature components in order x, y, xy
              :type curvatures: ndarray(dtype=float, dim=3,1)
              :param delta_T: Temperature difference
              :type delta_T: float
              :returns: mechanical_strains
              :rtype: ndarray(dtype=float, dim=3,2)

         """

        mechanical_strains = np.zeros((3, 2))

        mechanical_strains[:, 0, np.newaxis] = midplane_strains.components + self.lamina.coordinates[0] * curvatures.components
        mechanical_strains[:, 1, np.newaxis] = midplane_strains.components + self.lamina.coordinates[1] * curvatures.components

        if delta_T:
            mechanical_strains[:, 0, np.newaxis] -= self.lamina.global_properties.alpha * delta_T
            mechanical_strains[:, 1, np.newaxis] -= self.lamina.global_properties.alpha * delta_T

        if midplane_strains.strain_type == LoadType.thermal:
            self.thermal_strain = StrainState(mechanical_strains, self.coordinate_system, midplane_strains.strain_type)
            self.lamina.local_properties.compute_thermal_strains()

        elif midplane_strains.strain_type == LoadType.combined:
            self.total_strain = StrainState(mechanical_strains, self.coordinate_system, midplane_strains.strain_type)
            self.lamina.local_properties.compute_total_strains()

    def compute_mechanical_stress(self, strains):
        """Computes the mechanical stress caused by change in temperature delta_T

              :param strains: Strain array containing components in order x, y, xy
              :type strains: ndarray(dtype=float, dim=3,2)

              :returns: mechanical_stress
              :rtype: ndarray(dtype=float, dim=3,2)

         """
        mechanical_stress = np.zeros((3, 2))

        mechanical_stress[:, 0, np.newaxis] = self.lamina.global_properties.Q.dot(strains.components[:, 0, np.newaxis])
        mechanical_stress[:, 1, np.newaxis] = self.lamina.global_properties.Q.dot(strains.components[:, 1, np.newaxis])

        # Calculate stresses corresponding to strains
        if strains.strain_type == LoadType.thermal:

            self.thermal_stress.components[:, 0, np.newaxis] = mechanical_stress[:, 0, np.newaxis]
            self.thermal_stress.components[:, 1, np.newaxis] = mechanical_stress[:, 1, np.newaxis]
            self.lamina.local_properties.compute_thermal_stress()

        elif strains.strain_type == LoadType.combined:
            self.total_stress.components[:, 0, np.newaxis] = mechanical_stress[:, 0, np.newaxis]
            self.total_stress.components[:, 1, np.newaxis] = mechanical_stress[:, 1, np.newaxis]
            self.lamina.local_properties.compute_total_stress()




