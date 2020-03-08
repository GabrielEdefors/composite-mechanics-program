import numpy as np


class Laminate:
    """Class used to represent the laminate.

               :param laminae: List of lamina that make up the laminate
               :type laminae: List of instances of lamina

               :ivar moments: Moments per unit width [Mx, My, Mxy]
               :ivar normal_forces: Normal forces per unit width [Nx, Ny]
               :ivar delta_T: Temperature difference relative unstressed state
               :ivar thickness: Total thickness of the the laminate

     """
    def __init__(self, laminae):
        self.laminae = laminae
        self.moments = [0.0, 0.0, 0.0]
        self.normal_forces = [0.0, 0.0]
        self.delta_T = [0.0]
        self.thickness = sum([lamina.thickness for lamina in self.laminae])
        self.A, self.B, self.D = self.compute_stiffness_matrices()
        self.thermal_load_vector = np.zeros((6, 1))

    def add_laminae(self, laminae):
        self.laminae.append(laminae)

    def add_loads(self, **loads):
        """Adds loads to the laminate instance, support moments, normal forces and temperature loads

            :param \**loads:
                 See below

            :Keyword Arguments:
                 * *moments* (``list``) --
                 * *normal_forces* (``list``) --
                 * *delta_T* (``float``) --

         """

        if 'moments' in loads:
            self.moments = loads['moments']
        elif 'normal_forces' in loads:
            self.normal_forces = loads['normal_forces']
        elif 'delta_T' in loads:
            self.delta_T = loads['delta_T'][0]

    def compute_stiffness_matrices(self):
        """Computes A, B and D matrices

              :returns: A, B, D matrices
              :rtype: ndarray(dtype=float, dim=3,3))

         """

        A = np.zeros(shape=(3, 3))
        B = np.zeros(shape=(3, 3))
        D = np.zeros(shape=(3, 3))

        for lamina in self.laminae:

            A += lamina.global_properties.Ak
            B += lamina.global_properties.Bk
            D += lamina.global_properties.Dk

        return A, B, D

    def compute_thermal_stresses(self):
        """Computes thermal stresses and corresponding z coordinates

              :returns: mechanical_stress_global, mechanical_stress_local, z_coordinates
              :rtype: ndarray(dtype=float, dim=3,nr_laminae*2), ndarray(dtype=float, dim=nr_laminae*2)

         """

        # Compute thermal forces and moments ===========================================================================
        thermal_normal_forces = np.zeros(shape=(3, 1))
        thermal_moments = np.zeros(shape=(3, 1))

        for lamina in self.laminae:

            thermal_normal_forces += self.delta_T * lamina.global_properties.Ak.dot(lamina.global_properties.alpha)
            thermal_moments += self.delta_T * lamina.global_properties.Bk.dot(lamina.global_properties.alpha)

        # Calculate the mid-plane strains caused by the thermal forces and moments =====================================
        self.thermal_load_vector = np.array([thermal_normal_forces, thermal_moments]).reshape(6, 1)
        midplane_strains, curvatures = self.compute_strains(self.thermal_load_vector)

        # Compute mechanical stress caused by the thermal loads ========================================================
        mechanical_stress_global = np.zeros((3, len(self.laminae) * 2))
        mechanical_stress_local = np.zeros((3, len(self.laminae) * 2))
        z_coordinates = np.zeros((len(self.laminae) * 2))

        for index, lamina in enumerate(self.laminae):

            mechanical_strains = lamina.global_properties.compute_mechanical_strains(midplane_strains, curvatures, self.delta_T, type='thermal')

            # Stress
            mechanical_stress_global[:, (2*index):(2*index+2)] = \
                lamina.global_properties.compute_mechanical_stress(mechanical_strains, type='thermal')
            mechanical_stress_local[:, (2 * index):(2 * index + 2)] = lamina.local_properties.thermal_stress

            # Create two coordinates per interface, one per lamina
            z_coordinates[2*index], z_coordinates[2*index+1] = lamina.coordinates

        return mechanical_stress_global, mechanical_stress_local, z_coordinates

    def compute_total_stress(self):
        """Computes the total stress caused by both thermal and outer loading

              :returns: mechanical_stress_global, mechanical_stress_local, z_coordinates
              :rtype: ndarray(dtype=float, dim=3,nr_laminae*2), ndarray(dtype=float, dim=nr_laminae*2)

         """

        # Convert load vectors to numpy arrays
        normal_forces, moments = np.array(self.normal_forces).reshape(3, 1), np.array(self.moments).reshape(3, 1)

        mechanical_load_vector = np.concatenate((normal_forces, moments), axis=0)
        midplane_strains, curvatures = self.compute_strains(self.thermal_load_vector + mechanical_load_vector)

        # Compute mechanical stress caused by the total loads
        mechanical_stress_global = np.zeros((3, len(self.laminae) * 2))
        mechanical_stress_local = np.zeros((3, len(self.laminae) * 2))

        z_coordinates = np.zeros((len(self.laminae) * 2))

        for index, lamina in enumerate(self.laminae):

            mechanical_strains = lamina.global_properties.compute_mechanical_strains(midplane_strains, curvatures, type='total')

            # Compute stress
            mechanical_stress_global[:, (2*index):(2*index+2)] = \
                lamina.global_properties.compute_mechanical_stress(mechanical_strains, type='total')
            mechanical_stress_local[:, (2 * index):(2 * index + 2)] = lamina.local_properties.total_stress

            # Create two coordinates per interface, one per lamina
            z_coordinates[2*index], z_coordinates[2*index+1] = lamina.coordinates

        return mechanical_stress_global, mechanical_stress_local, z_coordinates

    def compute_strains(self, loads):
        """Computes strains for a certain outer load specified by loads

            :param loads: Load vector containing N and M
            :type loads: ndarray(dtype=float, dim=6)

            :returns: midplane_strains, curvatures
            :rtype: ndarray(dtype=float, dim=3)

         """

        total_stiffness_matrix = np.concatenate([np.concatenate((self.A, self.B), axis=1), np.concatenate((self.B, self.D), axis=1)])
        strains = np.linalg.solve(total_stiffness_matrix, loads)

        midplane_strains = strains[:3]
        curvatures = strains[3:]

        return midplane_strains, curvatures









