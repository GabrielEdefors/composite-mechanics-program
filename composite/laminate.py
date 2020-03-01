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
        self.A, self.B, self.D = self.compute_stiffness_matrices()           # Wrong B and D

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

        A = np.zeros(shape=(3, 3))
        B = np.zeros(shape=(3, 3))
        D = np.zeros(shape=(3, 3))

        for lamina in self.laminae:

            A += lamina.global_properties.Ak
            B += lamina.global_properties.Bk
            D += lamina.global_properties.Dk

        return A, B, D

    def compute_thermal_stresses(self):

        # Compute thermal forces and moments
        thermal_normal_forces = np.zeros(shape=(3, 1))
        thermal_moments = np.zeros(shape=(3, 1))

        for lamina in self.laminae:

            thermal_normal_forces += self.delta_T * lamina.global_properties.Ak.dot(lamina.global_properties.alpha)
            thermal_moments += self.delta_T * lamina.global_properties.Bk.dot(lamina.global_properties.alpha)

        # Calculate the mid-plane strains caused by the thermal forces and moments
        thermal_load_vector = np.array([thermal_normal_forces, thermal_moments]).reshape(6, 1)
        total_stiffness_matrix = np.concatenate([np.concatenate((self.A, self.B), axis=1), np.concatenate((self.B, self.D), axis=1)])
        midplane_strains = np.linalg.solve(total_stiffness_matrix, thermal_load_vector)

        # Compute mechanical strains caused by the thermal loads
        mechanical_stress_global = np.zeros((3, len(self.laminae) * 2))
        mechanical_stress_local = np.zeros((3, len(self.laminae) * 2))
        z_coordinates = np.zeros((len(self.laminae) * 2))

        for index, lamina in enumerate(self.laminae):

            lamina.stress.compute_mechanical_strains(midplane_strains[:3], midplane_strains[3:], self.delta_T)
            mechanical_stress_global[:, (2*index):(2*index+2)], mechanical_stress_local[:, (2*index):(2*index+2)] = lamina.stress.compute_mechanical_stress()
            z_coordinates[2*index], z_coordinates[2*index+1] = lamina.coordinates

        return mechanical_stress_global, mechanical_stress_local, z_coordinates








