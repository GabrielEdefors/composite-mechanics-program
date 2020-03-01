from composite import read_input_file, plot_stress
import matplotlib.pyplot as plt

# Read input file
filename = 'assignment_1.txt'
laminate = read_input_file(filename)

# Thermal stresses =====================================================================================================
thermal_stresses_global, thermal_stresses_local, z_coordinates = laminate.compute_thermal_stresses()

# Plot global stresses
axes_global = plt.subplots(nrows=1, ncols=3, constrained_layout=True, figsize=(10, 7))[1]
fig_global = plt.figure(1)
fig_global.suptitle('Global stresses in laminate', fontsize=16)
plot_stress(axes=axes_global, coordinates=[z_coordinates / 1e3, 'm'], stress=[thermal_stresses_global / 1e6, 'MPa'],
            stresstype='global')

# Plot local stresses
axes_local = plt.subplots(nrows=1, ncols=3, constrained_layout=True, figsize=(10, 7))[1]
fig_local = plt.figure(2)
fig_local.suptitle('Local stresses in laminate', fontsize=16)
plot_stress(axes=axes_local, coordinates=[z_coordinates / 1e3, 'm'], stress=[thermal_stresses_local / 1e6, 'MPa'],
            stresstype='local')

plt.show()

#


