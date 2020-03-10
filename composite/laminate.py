import numpy as np
from strain import StrainState
from stress import StressState
from coordinate_systems import CoordinateSystem
from enum import Enum


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
        self.thickness = sum([lamina.thickness for lamina in self.laminae])
        self.coordinate_system = CoordinateSystem.xy

        # Loads
        self.moments = [0.0, 0.0, 0.0]
        self.normal_forces = [0.0, 0.0]
        self.delta_T = [0.0]
        self.thermal_load_vector = np.zeros((6, 1))

        # Initiate stiffness matrices
        self.A, self.B, self.D = self.compute_stiffness_matrices()

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

    def compute_thermal_forces(self):
        """Computes thermal forces acting on the laminate

        """

        # Compute thermal forces and moments ===========================================================================
        thermal_normal_forces = np.zeros(shape=(3, 1))
        thermal_moments = np.zeros(shape=(3, 1))

        for lamina in self.laminae:
            thermal_normal_forces += self.delta_T * lamina.global_properties.Ak.dot(lamina.global_properties.alpha)
            thermal_moments += self.delta_T * lamina.global_properties.Bk.dot(lamina.global_properties.alpha)

        self.thermal_load_vector[:3] = thermal_normal_forces
        self.thermal_load_vector[3:] = thermal_moments

    def compute_thermal_stress(self):

        # Compute the thermal load vector
        self.compute_thermal_forces()

        # Calculate the mid-plane strains caused by the thermal forces and moments
        midplane_strains, curvatures = self.compute_strains(self.thermal_load_vector, LoadType.thermal)

        for index, lamina in enumerate(self.laminae):

            # Compute global strains in lamina
            lamina.global_properties.compute_mechanical_strains(midplane_strains, curvatures, self.delta_T)

            # Compute global and local stress in lamina
            lamina.global_properties.compute_mechanical_stress(lamina.global_properties.thermal_strain)

    def compute_total_stress(self):
        """Computes the total stress caused by both thermal and outer loading

              :returns: mechanical_stress_global, mechanical_stress_local, z_coordinates
              :rtype: ndarray(dtype=float, dim=3,nr_laminae*2), ndarray(dtype=float, dim=nr_laminae*2)

         """

        # Convert load vectors to numpy arrays
        normal_forces, moments = np.array(self.normal_forces).reshape(3, 1), np.array(self.moments).reshape(3, 1)
        mechanical_load_vector = np.concatenate((normal_forces, moments), axis=0)
        total_load = self.thermal_load_vector + mechanical_load_vector

        # Calculate the mid-plane strains caused by the thermal forces and moments
        midplane_strains, curvatures = self.compute_strains(total_load, LoadType.total)

        for index, lamina in enumerate(self.laminae):
            # Compute global strains in lamina
            lamina.global_properties.compute_mechanical_strains(midplane_strains, curvatures)

            # Compute global and local stress in lamina
            lamina.global_properties.compute_mechanical_stress(lamina.global_properties.total_strain)

    def create_laminate_arrays(self, load_type):

        # Initiate stress, strain and coordinates
        components_global = np.zeros((3, len(self.laminae) * 2))
        components_local = np.zeros((3, len(self.laminae) * 2))
        z_coordinates = np.zeros((len(self.laminae) * 2))

        if load_type == LoadType.thermal:
            mechanical_stress_global = StressState(components_global, self.coordinate_system, LoadType.thermal)
            mechanical_stress_local = StressState(components_local, CoordinateSystem.LT, LoadType.thermal)
        else:
            mechanical_stress_global = StressState(components_global, self.coordinate_system, LoadType.total)
            mechanical_stress_local = StressState(components_local, CoordinateSystem.LT, LoadType.total)

        # Compute mechanical stress caused by the total loads
        for index, lamina in enumerate(self.laminae):

            if load_type == LoadType.thermal:
                mechanical_stress_global.components[:, (2 * index):(2 * index + 2)] = lamina.global_properties.thermal_stress.components
                mechanical_stress_local.components[:, (2 * index):(2 * index + 2)] = lamina.local_properties.thermal_stress.components

            elif load_type == LoadType.total:
                mechanical_stress_global.components[:, (2 * index):(2 * index + 2)] = lamina.global_properties.total_stress.components
                mechanical_stress_local.components[:, (2 * index):(2 * index + 2)] = lamina.local_properties.total_stress.components

            # Create two coordinates per interface, one per lamina
            z_coordinates[2 * index], z_coordinates[2 * index + 1] = lamina.coordinates

        return mechanical_stress_global, mechanical_stress_local, z_coordinates

    def compute_strains(self, loads, strain_type):
        """Computes strains for a certain outer load specified by loads

            :param loads: Load vector containing N and M
            :type loads: ndarray(dtype=float, dim=6,1)
            :param strain_type: Either thermal or total
            :type strain_type: Enum

            :returns: midplane_strains, curvatures
            :rtype: ndarray(dtype=float, dim=3,1)

         """

        total_stiffness_matrix = np.concatenate([np.concatenate((self.A, self.B), axis=1), np.concatenate((self.B, self.D), axis=1)])
        strains = np.linalg.solve(total_stiffness_matrix, loads)

        midplane_strains = StrainState(strains[:3], self.coordinate_system, strain_type)
        curvatures = StrainState(strains[3:], self.coordinate_system, strain_type)

        return midplane_strains, curvatures


class LoadType(Enum):
    thermal = 1
    total = 2

    def __eq__(self, other):
        return self.value == other.value









