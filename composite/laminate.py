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

            A += lamina.Q_global.dot(lamina.coordinates[1] - lamina.coordinates[0])
            B += 1/2 * lamina.Q_global.dot(lamina.coordinates[1] ** 2 - lamina.coordinates[0] ** 2)
            D += 1/3 * lamina.Q_global.dot(lamina.coordinates[1] ** 3 - lamina.coordinates[0] ** 3)

        return A, B, D





