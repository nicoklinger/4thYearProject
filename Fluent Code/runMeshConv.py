import ansys.fluent.core as pyfluent
from generateFluentMesh import generate_fluent_mesh
from CreateMeshBoolean import create_mesh
from runSim import run_sim
import numpy as np
import os
import csv
import pandas as pd
#import telebot
def run_mesh_conv(version, n_processor, is_gui, re_mesh_conv, area_ref,
                  length_ref, res_tol, n_iterations, mesh_conv_dir, start_mesh_size, step_size, n_sim,
                  geometry_file_path, AssyName, json_file_path,
                  use_fluent_meshing=False, cleanup_on_exit=False):
    # Runs mesh convergence
    is_mesh_conv = True

    # Constants
    RHO = 1.225             # kg / m3
    MU = 1.7894e-05         # Ns / m2

    # Re and speed
    v_inlet = (re_mesh_conv * MU) / (length_ref * RHO)

    # Mesh Size Array
    mesh_array = start_mesh_size + np.arange(0, n_sim) * -step_size

    # Fixed mesh size
    element_size_general_array = start_mesh_size*180 + np.arange(0, n_sim) * -step_size*233
    element_size_boi_array = start_mesh_size*80 + np.arange(0, n_sim) * -step_size*100

    with open(f"{mesh_conv_dir}\\ConvElementsSizes.csv", 'a') as f:
        writer = csv.writer(f)
        writer.writerow(zip(element_size_general_array, element_size_boi_array, mesh_array))

    for k in element_size_general_array:
        if k <= 0:
            print("At least 1 of the elements of the general mesh size is negative. Please fix. \n Aborting mesh_conv")
            return
    for k in element_size_boi_array:
        if k <= 0:
            print("At least 1 of the elements of the BOI mesh size is negative. Please fix. \n Aborting mesh_conv")
            return

    mesh_elements_array = []
    cd_array = []

    # Mesh
    j = 0
    for m in mesh_array:

        iteration_dir = mesh_conv_dir + '\\' + str(m).replace('.', '')
        project_file_path = iteration_dir.replace('\\', '\\\\\\\\') + '\\\\\\\\' + AssyName + '.mechdat'
        mesh_file_path = iteration_dir.replace('\\', '\\\\\\\\') + '\\\\\\\\' + AssyName + '.msh'

        if not os.path.isdir(iteration_dir):
            os.makedirs(iteration_dir)

        # if mesh file was not produced, launch meshing, otoherwise read the elements number from the file
        if not os.path.isfile(mesh_file_path.replace('\\\\\\\\','\\')):
            elements_number = create_mesh(geometry_file_path, project_file_path, mesh_file_path,
                                          element_size_general_array[j], element_size_boi_array[j],
                                          m, json_file_path)
            mesh_elements_array.append(elements_number)
           # bot.send_message(chat_id, f"Mesh created for the following design and elements sizes:\n{AssyName},\n{element_size_general_array[j]},\n{element_size_boi_array[j]}")
        elif os.path.isfile(os.path.dirname(mesh_file_path.replace('\\\\\\\\','\\'))+'mesh_features.txt'):
            with open(os.path.dirname(mesh_file_path.replace('\\\\\\\\','\\'))+'elements_number.txt', "r") as f:
                mesh_features = f.read()
            if mesh_features == f"{element_size_general_array[j]}, {element_size_boi_array[j]},{m}" and os.path.isfile(os.path.dirname(mesh_file_path.replace('\\\\\\\\','\\'))+'elements_number.txt'):
                    with open(os.path.dirname(mesh_file_path.replace('\\\\\\\\','\\'))+'elements_number.txt', "r") as f:
                        elements_number = f.read()
        else:
            print("ERROR: Mesh file has already been created but no info on the number of elements or mesh features was saved.\n"
                  "Create a elements_number.txt file with the number of elements and re-run this iteration.\n"
                  "Aborting this iteration ...\n\n")

            return

        if use_fluent_meshing:
            meshing_session = generate_fluent_mesh(version, n_processor, iteration_dir, mesh_file_path.replace('\\\\\\\\', '\\'),
                                               is_gui)
            solver = meshing_session.switch_to_solver()
        else:
            solver = pyfluent.launch_fluent(product_version=version,
                                            mode="solver",
                                            show_gui=is_gui,
                                            version="3d",
                                            precision="double",
                                            processor_count=n_processor,
                                            cleanup_on_exit=cleanup_on_exit)
            solver.tui.file.read_case(mesh_file_path.replace('\\\\\\\\','\\'))

        report_file_name = run_sim(solver, v_inlet, area_ref, length_ref, res_tol, n_iterations, 0, iteration_dir)
        
        df = pd.read_csv(report_file_name)
        i = 1
        cd = []
        while i <= round(n_iterations/10):
            a = df.iloc[-i]
            a = str(a)
            list = [str(x) for x in a.split()]
            cd.append(float(list[2]))
            i += 1

        avg_cd = sum(cd) / len(cd)
        cd_array.append(avg_cd)
        with open(f'{iteration_dir}\\mesh_info.txt', 'w') as f:
            text = f"{elements_number}, {avg_cd}"
            f.write(text)
        with open(f'{mesh_conv_dir}\\ConvElementSizes-so_far.csv', 'a') as f:
            writer = csv.writer(f, delimiter=',', lineterminator='\n')
            writer.writerow({elements_number, avg_cd})

        j += 1

    return mesh_elements_array, cd_array


