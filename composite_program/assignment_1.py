from composite import read_input_file, plot_stress, FilePrint, LoadType
import matplotlib.pyplot as plt

# Read input file
filename = 'assignment_1.txt'
laminate, project_info = read_input_file(filename=filename)

# Thermal stresses =====================================================================================================
laminate.compute_thermal_stress()
thermal_stresses_global, thermal_stresses_local, thermal_strains_global, thermal_strains_local, z_coordinates = laminate.create_laminate_arrays(LoadType.thermal)

# Plot global stresses
axes_global = plt.subplots(nrows=1, ncols=3, constrained_layout=True, figsize=(10, 7))[1]
fig_global = plt.figure(1)
fig_global.suptitle('Global stresses in laminate', fontsize=16)
plot_stress(axes=axes_global, coordinates=z_coordinates, quantity=thermal_stresses_global)

# Plot local stresses
axes_local = plt.subplots(nrows=1, ncols=3, constrained_layout=True, figsize=(10, 7))[1]
fig_local = plt.figure(2)
fig_local.suptitle('Local stresses in laminate', fontsize=16)
plot_stress(axes=axes_local, coordinates=z_coordinates, quantity=thermal_stresses_local)

# Total stress =========================================================================================================
laminate.compute_total_stress()
total_stresses_global, total_stresses_local, total_strains_global, total_strains_local, z_coordinates = laminate.create_laminate_arrays(LoadType.combined)

# Plot global stresses
axes_global = plt.subplots(nrows=1, ncols=3, constrained_layout=True, figsize=(10, 7))[1]
fig_global = plt.figure(3)
fig_global.suptitle('Global stresses in laminate', fontsize=16)
plot_stress(axes=axes_global, coordinates=z_coordinates, quantity=total_stresses_global)

# Plot local stresses
axes_local = plt.subplots(nrows=1, ncols=3, constrained_layout=True, figsize=(10, 7))[1]
fig_local = plt.figure(4)
fig_local.suptitle('Local stresses in laminate', fontsize=16)
plot_stress(axes=axes_local, coordinates=z_coordinates, quantity=total_stresses_local)

# Plot global stresses
axes_global = plt.subplots(nrows=1, ncols=3, constrained_layout=True, figsize=(10, 7))[1]
fig_global = plt.figure(5)
fig_global.suptitle('Global strains in laminate', fontsize=16)
plot_stress(axes=axes_global, coordinates=z_coordinates, quantity=total_strains_global)

plt.show()

# Write results to file ================================================================================================
filename = 'stress'
printobj = FilePrint({'PROJECT_INFO': project_info}, filename)
printobj.print_project_info()
printobj.print_output_data(laminate, load_type=LoadType.thermal)
printobj.print_output_data(laminate, load_type=LoadType.combined)


