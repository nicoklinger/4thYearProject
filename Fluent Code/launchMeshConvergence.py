import sys

print("Script started. Importing all modules ... \n")

from runMeshConv import run_mesh_conv
from CreateGeometryBoolean import create_assembly
import os
import json, csv
import numpy as np
import matplotlib.pyplot as plt

# Set type of geometry file
create_array_manually = False

use_automatically_created_geometry = False
manual_design_name = "Validation10AR"   # Variable will be used only if above boolean is False

# Set geometry iterations numbers
iteration_param = [0,                   # Iterations of r    (number corresponds to number of iterations)
                   0,                   # Iterations of h   (number corresponds to number of iterations)
                   0,                   # Iterations of t   (number corresponds to number of iterations)
                   0,                   # Iterations of spokes (any number != 0)
                   0]                   # Iterations of circles (any number != 0)
#change if you want to start mesh conv from different index than 0
j=7
# Set parameters for seed geometry file
# The following is start + end parameter. If no iteration is desired, only start param is considered


## OUtisde r iterations are not implemented yet.
if not create_array_manually:       
    r = [200/2, 50]                    # Seed diameter in mm
    h = [0.5, 0.05]                   # Seed high in mm
    t = [1.5, 1]                   # Thickness of spokes in mm
    inside_r = [80/2, 30]
    spokes = [212, 22]               # Number of spokes in the seed
    circles = [0, 4]                # Number of concentric circles
    outside_r = [0, 100/2]
    angle = [0, 15]
else:
    r = [22/2, 90/2]
    h = [0.5, 0.5]                   # Seed high in mm
    t = [0.3, 1.5]                   # Thickness of spokes in mm
    inside_r = [11/2, 22.5/2]
    outside_r = [44/2, 100/2]
    spokes = [82, 30]               # Number of spokes in the seed
    circles = [0, 0]                # Number of concentric circles

# Define parameters of mesh convergence
re_mesh_conv = 50              # Reynolds number of mesh conv
n_sim = 19                      # Number of iterations in mesh conv
res_tol = 1e-6                  # Tolerance of fluent resolution
n_iterations = 125               # Number of iteration in fluent solution

# Set iteration mode
if any(iteration_param) != 0 and use_automatically_created_geometry:
    print("Geometry iteration mode is ON \n")
    geom_iteration_mode = True
elif any(iteration_param) == 0 and not use_automatically_created_geometry:
    print("Geometry iteration mode is OFF (using a manually created design) \n")
    geom_iteration_mode = False
elif any(iteration_param) == 0 and use_automatically_created_geometry:
    print("Geometry iteration mode is OFF (using an automatically created design) \n")
    geom_iteration_mode = False
elif any(iteration_param) != 0 and not use_automatically_created_geometry:
    print("ERROR: iteration mode is ON but manually created design was selected. \n Aborting ...")
    sys.exit()

# Get current working directory
folder = os.getcwd()
folder4 = folder.replace('\\', '\\\\\\\\')

def mesh_conv_of_1design(AssyName, re_mesh_conv, n_sim, res_tol, n_iterations):
    geometry_file_path = folder.replace('\\','\\\\') + "\\\\Sims\\\\" + AssyName + "\\\\" + AssyName + ".step"
    json_file_path = geometry_file_path.replace("step","json")

    with open(json_path) as f:
        geom_data = json.load(f)

    area_ref = geom_data['surf_area'] / 10 ** 6  # Seed projected area in mm2
    length_ref = (geom_data['seed_radius']) * 2 / 1000  # Seed radius in mm
    height_ref = geom_data['seed_height'] / 1000  # Seed height in mm
    thick_ref = geom_data['spokes_thickness'] / 1000  # Thickness of spokes in mm

    mesh_conv_dir = f"{folder}\\Sims\\{AssyName}\\MeshConv"

    if not os.path.isdir(mesh_conv_dir):
        os.makedirs(mesh_conv_dir)

    version = "23.1.0"
    n_processor = 16
    is_gui = False

    start_mesh_size = min(height_ref, thick_ref)
    step_size = start_mesh_size / 25

    elements_array, cd_array = run_mesh_conv(version, n_processor, is_gui, re_mesh_conv, area_ref,
                  length_ref, res_tol, n_iterations, mesh_conv_dir, start_mesh_size, step_size, n_sim,
                  geometry_file_path, AssyName, json_file_path, cleanup_on_exit=True)

    # Save results of mesh convergence in a file in the MeshConv folder
    with open(f"{mesh_conv_dir}\\ConvInfo.csv", "a") as f:
        writer = csv.writer(f, delimiter=',', lineterminator='\n')
        writer.writerow(zip(elements_array, cd_array))

    plt.plot(elements_array, cd_array)
    plt.savefig(f"{mesh_conv_dir}\\ConvCurve.png")

# If iteration mode is on, create multiple designs, otherwise create 1 design or use design already created
if geom_iteration_mode and not create_array_manually:
    j = 0
    for i in iteration_param:
        j += 1
        if i != 0:
            to_iterate = j

    if to_iterate == 1:
        # iterate r

        # specify number of iterations
        reps = iteration_param[0]
        # create array for values
        r = np.linspace(r[0], r[1], reps)

        # Create design for every value in above array and do mesh convergence on it
        for i in r:

            # Define file name and paths
            AssyName = f"AssySeed_{h[0]}h_{i}r_{t[0]}t_{spokes[0]}spokes_{circles[0]}Circles_{inside_r[0]}InsideR_{outside_r[0]}OutsideR".replace('.', '')
            geometry_file_path = folder + "\\Sims\\" + AssyName + "\\" + AssyName + ".step"
            json_path = geometry_file_path.replace('step', 'json')

            print(f"Generated file {AssyName}, executing mesh convergence on it")

            #  Creates single geometry file for iteration
            create_assembly(t=t[0], r=i, h=h[0], spokes=spokes[0], circles=circles[0], inside_r=inside_r[0], outside_r=outside_r[0])

            # Runs mesh convergence for this geometry file
            try:
                mesh_conv_of_1design(AssyName, re_mesh_conv, n_sim, res_tol, n_iterations)
            except Exception as e:
                print(f"Error in design {AssyName}: {e}")

    elif to_iterate == 2:
        # iterate h

        # specify number of iterations
        reps = iteration_param[1]
        # create array for values
        h = np.linspace(h[0], h[1], reps)

        # Create design for every value in above array and do mesh convergence on it
        for i in h:
            # Define file name and paths
            AssyName = f"AssySeed_{i}h_{r[0]}r_{t[0]}t_{spokes[0]}spokes_{circles[0]}Circles_{inside_r[0]}InsideR_{outside_r[0]}OutsideR".replace('.', '')
            geometry_file_path = folder + "\\Sims\\" + AssyName + "\\" + AssyName + ".step"
            json_path = geometry_file_path.replace('step', 'json')

            print(f"Generated file {AssyName}, executing mesh convergence on it")

            #  Creates single geometry file for iteration
            create_assembly(t=t[0], r=r[0], h=i, spokes=spokes[0], circles=circles[0], inside_r=inside_r[0], outside_r=outside_r[0])

            # Runs mesh convergence for this geometry file
            try:
                mesh_conv_of_1design(AssyName, re_mesh_conv, n_sim, res_tol, n_iterations)
            except Exception as e:
                print(f"Error in design {AssyName}: {e}")
                
    elif to_iterate == 3:
        # iterate t

        # specify number of iterations
        reps = iteration_param[2]

        # create array for values
        t = np.linspace(t[0], t[1], reps)
    
        # Create design for every value in above array and do mesh convergence on it
        for i in t:
            print(f"t={i}")
            # Define file name and paths
            AssyName = f"AssySeed_{h[0]}h_{r[0]}r_{i}t_{spokes[0]}spokes_{circles[0]}Circles_{inside_r[0]}InsideR_{outside_r[0]}OutsideR".replace('.', '')
            geometry_file_path = folder + "\\Sims\\" + AssyName + "\\" + AssyName + ".step"
            json_path = geometry_file_path.replace('step', 'json')

            print(f"Generated file {AssyName}, executing mesh convergence on it")

            #  Creates single geometry file for iteration
            create_assembly(t=i, r=r[0], h=h[0], spokes=spokes[0], circles=circles[0], inside_r=inside_r[0], outside_r=outside_r[0])

            # Runs mesh convergence for this geometry file
            try:
                mesh_conv_of_1design(AssyName, re_mesh_conv, n_sim, res_tol, n_iterations)
            except Exception as e:
                print(f"Error in design {AssyName}: {e}")

    elif to_iterate == 4:
        # iterate circles

        # create array for values
        circles = np.arange(circles[0], circles[1], dtype=int)
        # specify number of iterations
        reps = len(circles)

        # Create design for every value in above array and do mesh convergence on it
        for i in circles:
            # Define file name and paths
            AssyName = f"AssySeed_{h[0]}h_{r[0]}r_{t[0]}t_{spokes[0]}spokes_{i}Circles_{inside_r[0]}InsideR_{outside_r[0]}OutsideR".replace('.', '')
            geometry_file_path = folder + "\\Sims\\" + AssyName + "\\" + AssyName + ".step"
            json_path = geometry_file_path.replace('step', 'json')

            print(f"Generated file {AssyName}, executing mesh convergence on it")

            #  Creates single geometry file for iteration
            create_assembly(t=t[0], r=r[0], h=h[0], spokes=spokes[0], circles=i, inside_r=inside_r[0], outside_r=outside_r[0])

            # Runs mesh convergence for this geometry file
            try:
                mesh_conv_of_1design(AssyName, re_mesh_conv, n_sim, res_tol, n_iterations)
            except Exception as e:
                print(f"Error in design {AssyName}: {e}")
                
    elif to_iterate == 5:
        # iterate spokes

        # create array for values
        spokes = np.arange(spokes[0], spokes[1], dtype=int)
        # specify number of iterations
        reps = len(spokes)

        # Create design for every value in above array and do mesh convergence on it
        for i in spokes:
            # Define file name and paths
            AssyName = f"AssySeed_{h[0]}h_{r[0]}r_{t[0]}t_{i}spokes_{circles[0]}Circles_{inside_r[0]}InsideR_{outside_r[0]}OutsideR".replace('.', '')
            geometry_file_path = folder + "\\Sims\\" + AssyName + "\\" + AssyName + ".step"
            json_path = geometry_file_path.replace('step', 'json')

            print(f"Generated file {AssyName}, executing mesh convergence on it")

            #  Creates single geometry file for iteration
            create_assembly(t=t[0], r=r[0], h=h[0], spokes=i, circles=circles[0], inside_r=inside_r[0], outside_r=outside_r[0])

            # Runs mesh convergence for this geometry file
            try:
                mesh_conv_of_1design(AssyName, re_mesh_conv, n_sim, res_tol, n_iterations)
            except Exception as e:
                print(f"Error in design {AssyName}: {e}")
elif not geom_iteration_mode and create_array_manually:
    print("I will iterate the manually inputted array")
    k=0
    for i in inside_r:
        # Define file name and paths
        AssyName = f"AssySeed_{h[k]}h_{r[k]}r_{t[k]}t_{spokes[k]}spokes_{circles[k]}Circles_{inside_r[k]}InsideR_{outside_r[k]}OutsideR".replace('.', '')
        geometry_file_path = folder + "\\Sims\\" + AssyName + "\\" + AssyName + ".step"
        json_path = geometry_file_path.replace('step', 'json')

        print(f"Generated file {AssyName}, executing mesh convergence on it")

        #  Creates single geometry file for iteration
        create_assembly(t=t[k], r=r[k], h=h[k], spokes=spokes[k], circles=circles[k], inside_r=inside_r[k], outside_r=outside_r[k])

        # Runs mesh convergence for this geometry file
        try:
            mesh_conv_of_1design(AssyName, re_mesh_conv, n_sim, res_tol, n_iterations)
        except Exception as e:
            print(f"Error in design {AssyName}: {e}")
        k += 1
        
    
elif not geom_iteration_mode and not create_array_manually:
    # when geometry iteration mode is off:

    # set file name
    if use_automatically_created_geometry == True:
        AssyName = f"AssySeed_{h[0]}h_{r[0]}r_{t[0]}t_{spokes[0]}spokes_{circles[0]}Circles_{inside_r[0]}InsideR_{outside_r[0]}OutsideR_{angle[0]}Degrees".replace('.','')
    else:
        AssyName = f"Assy{manual_design_name}"

    # Define paths automatically
    geometry_file_path = folder + "\\Sims\\" + AssyName + "\\" + AssyName + ".step"
    json_path = geometry_file_path.replace('step', 'json')

    print(f"Geometry Iteration mode is turned OFF. The step file is {AssyName}")

    # if necessary, create geometry file and then execute mesh convergence function
    if not os.path.isfile(geometry_file_path) and use_automatically_created_geometry:
        print("Creating geometry file ... \n")

        #  Creates single geometry file for iteration
        create_assembly(t=t[0], r=r[0], h=h[0], spokes=spokes[0], circles=circles[0], inside_r=inside_r[0], outside_r=outside_r[0], rotation_angle=angle[0])

        # Runs mesh convergence for this geometry file
        try:
            mesh_conv_of_1design(AssyName, re_mesh_conv, n_sim, res_tol, n_iterations)
        except Exception as e:
            print(f"Error in design {AssyName}: {e}")

    elif not os.path.isfile(geometry_file_path) and not use_automatically_created_geometry:
        print("Manually created file was not found. \n"
              "Have you executed the script launchCreateGeometry-ManualMode.py before this script?")

    elif os.path.isfile(geometry_file_path):
        print("Geometry file already exists. Running mesh convergence on it ... \n")
        # File already exists, run mesh convergence straightaway
        mesh_conv_of_1design(AssyName, re_mesh_conv, n_sim, res_tol, n_iterations)

