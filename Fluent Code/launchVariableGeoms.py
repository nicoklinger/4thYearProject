from CreateMeshBoolean import create_mesh
from CreateGeometryBoolean import create_assembly
from runSim_transient import run_sim
import os
import json, csv
import numpy as np
import ansys.fluent.core as pyfluent

# Geometry parameters
r = [77/2 - 1.5]                       # Filament radius in mm
inside_r = [55/2]                 # Inside radius in mm
outside_r = [77/2]              # Outside radius in mm
h = [0.5]                       # Seed high in mm
t = [1.5]                        # Thickness of spokes in mm
spokes = [80]                     # Number of spokes in the seed
circles = [0]                     # Number of concentric circles

angle = 30

folder = os.getcwd()

# Mesh parameters - (get from info txt of converged mesh of this design)
element_size_general, element_size_boi, element_size_seed = 0.01544, 0.008, 0.00018

# Simulation Reynolds
Re = 8100

# Constants
RHO = 1.225             # kg / m3
MU = 1.7894e-05         # Ns / m2
res_tol = 1e-6
is_gui = False


# Iterate for all angles
i=0
while i < len(r):
    print(f"iterating angle {i} degrees")
    # Create the gemoetry
    create_assembly(t=t[i], r=r[i], h=h[i], inside_r=inside_r[i], spokes=spokes[i], circles=circles[i], outside_r=outside_r[i], rotation_angle=angle)
    AssyName = f"AssySeed_{h[i]}h_{r[i]}r_{t[i]}t_{spokes[i]}spokes_{circles[i]}Circles_{inside_r[i]}InsideR_{outside_r[i]}OutsideR_{angle}degrees".replace('.', '')
    
    print(f"Geometry created {AssyName}")

    geometry_file_path = folder.replace('\\','\\\\') + "\\\\Sims\\\\" + AssyName + "\\\\" + AssyName + ".step"
    json_file_path = folder.replace('\\','\\\\') + "\\\\Sims\\\\" + AssyName + "\\\\" + AssyName + ".json"

    mesh_file_path = folder.replace('\\','\\\\\\\\') + "\\\\\\\\Sims\\\\\\\\" + AssyName + "\\\\\\\\" + AssyName + ".msh"
    project_file_path = folder.replace('\\','\\\\\\\\') + "\\\\\\\\Sims\\\\\\\\" + AssyName + "\\\\\\\\" + AssyName + ".mechdat"

    # Create the mesh
    if not os.path.isfile(mesh_file_path.replace('\\\\\\\\','\\')):
        create_mesh(geometry_file_path, project_file_path, mesh_file_path,
                                          element_size_general, element_size_boi, element_size_seed, json_file_path)

        print("Mesh created")
    else:
        print("Mesh already present")
        

    print("Starting Fluent sim")
    # Run the simulation on Fluent
    iteration_dir = folder + '\\Sims\\'+ AssyName +'\\Reynolds\\' + str(Re).replace('.', '_')
    if not os.path.isdir(iteration_dir):
        os.makedirs(iteration_dir)
    with open(json_file_path) as f:
        geom_data = json.load(f)
        
    solver = pyfluent.launch_fluent(product_version="23.1.0",
                                            mode="solver",
                                            show_gui=False,
                                            version="3d",
                                            precision="double",
                                            processor_count=16,
                                            cleanup_on_exit=True)
    solver.tui.file.read_case(mesh_file_path.replace('\\\\\\\\','\\'))



    area_ref = geom_data['surf_area'] / 10 ** 6                 # Seed projected area in mm2
    area_ref_projected = area_ref * np.cos(np.deg2rad(i))      # Projected area
    length_ref = (geom_data['seed_radius'])*2/1000              # Seed diameter in mm


    v_inlet = (Re * MU) / (length_ref * RHO)

    idx = 0
        
    run_sim(solver, v_inlet, area_ref, length_ref, res_tol, idx, iteration_dir, reynolds_is_iter=True)

    i += 1

