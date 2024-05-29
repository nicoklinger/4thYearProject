from CreateGeometryBoolean import create_assembly
from CreateMeshBoolean import create_mesh
from runSim import run_sim
import cadquery as cq
import os
import json
import numpy as np
from math import pi

folder_dir = os.getcwd() + "\\ManualSims"
design_full_name = "Nylon threads.step"
computer_os="Windows"

if not os.path.isdir(folder_dir):
            os.makedirs(folder_dir)

# Element sizes
element_size_general = 0.1
element_size_boi = 0.01
element_size_seed = 0.0001

# Directories
design_name = design_full_name.replace('.step','')
design_folder = f"{folder_dir}\\{design_name}"
design_dir = design_folder + f"\\{design_full_name}"
if not os.path.isdir(design_folder):
            os.makedirs(design_folder)
            
project_file_path = design_dir.replace('\\','\\\\\\\\').replace('.step','.mechdat')
mesh_file_path = design_dir.replace('\\','\\\\\\\\').replace('.step','.msh')

# Save data to JSON file stored in same folder as Assy
r = 25e-3
h = 4e-3
area = 390.166e-6
json_data = {"surf_area":area,
             "seed_radius":r,
             "seed_height":h,
             "porosity":(pi*r**2-area)/(pi*r**2)}

if computer_os == "Mac":
    json_path = design_folder.replace('\\','/') + "/" + f"{design_name}.json"
else:
    json_path = design_folder + "\\" + f"{design_name}.json"
with open(json_path, 'w') as f:
    json.dump(json_data, f)

# Create Mesh File
create_mesh(design_dir, project_file_path, mesh_file_path,
                element_size_general, element_size_boi, element_size_seed, json_path)


