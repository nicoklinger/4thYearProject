from runReynoldsSim import run_reynolds_sim
import os
import json

# Get current working directory
folder = os.getcwd()
folder4 = folder.replace('\\', '\\\\\\\\')

# Wanted Geometry directory
AssyName = "AssyValidation10AR"
geometry_file_path = folder + "\\Sims\\" + AssyName + "\\" + AssyName + ".step"

# Read geometry json
json_path = geometry_file_path.replace('step', 'json')
with open(json_path) as f:
    geom_data = json.load(f)

area_ref = geom_data['surf_area']/10**6                 # Seed projected area in mm2

if "outside_r" in geom_data:
    length_ref = (geom_data['outside_r'])*2/1000
else:
    length_ref = (geom_data['seed_radius'])*2/1000          # Seed diameter in mm
height_ref = geom_data['seed_height']/1000              # Seed heigh in mm
thick_ref = geom_data['spokes_thickness']/1000          # Thickness of spokes in mm

# Create folder to store sims if not present
sims_dir = f"{folder}\\Sims\\{AssyName}\\Reynolds"
if not os.path.isdir(sims_dir):
    os.makedirs(sims_dir)

# Coverged Mesh path
converged_mesh = "conv_9999999999999999e-05"
mesh_file_path = folder + "\\Sims\\" + AssyName + "\\MeshConv\\" + converged_mesh + "\\" + AssyName + ".msh"

# Sims settings
is_gui = False
re_min = 1000
re_max = 1000
n_points = 1
start_id = 0 # Set as 0 if you want to start from the first Re

# Launch Simulation Loop
run_reynolds_sim(re_min, re_max, n_points, area_ref, length_ref, 
                 sims_dir, mesh_file_path, is_gui, start_id)
