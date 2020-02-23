

class Laminate:
    """Class used to represent the laminate.

               :param laminae: List of lamina that make up the laminate
               :type laminae: List of instances of lamina
               :param moments: Moments per unit width [Mx, My, Mxy]
               :type moments: List of floats
               :param normal_forces: Normal forces per unit width [Nx, Ny]
               :type moments: List of floats
               :param delta_T: Temperature difference relative unstressed state
               :type moments: float

     """
    def __init__(self, laminae):
        self.laminae = laminae
        self.moments = [0.0, 0.0, 0.0]
        self.normal_forces = [0.0, 0.0]
        self.delta_T = [0.0]

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







