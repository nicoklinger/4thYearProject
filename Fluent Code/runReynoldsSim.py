import numpy as np
from runSim_transient import run_sim
import os
import ansys.fluent.core as pyfluent

def run_reynolds_sim(re_min, re_max, n_points, area_ref, length_ref, 
                     sims_dir, mesh_path, is_gui, start_id):
    # Runs sims changing the reynolds number

    # Constants
    RHO = 1.225             # kg / m3
    MU = 1.7894e-05         # Ns / m2
    res_tol = 1e-6

    # Reynolds number and speeds
    Re = np.linspace(re_min, re_max, n_points, endpoint = True)
    v_inlet = (Re * MU) / (length_ref * RHO)
    v_inlet = v_inlet[start_id:len(v_inlet)]

    # Sims Loop
    idx = 0
    for v in v_inlet:

        v = round(v,5)
        
        # Create Sim folder
        iteration_dir = sims_dir + '\\' + str(Re[start_id]).replace('.', '_')
        if not os.path.isdir(iteration_dir):
            os.makedirs(iteration_dir)

        print("Running Sim at Re = " + str(Re[start_id]) + " and V = " + str(v))
        # Start Solver and Read Mesh
        if idx == 0:
            solver = pyfluent.launch_fluent(product_version="23.1.0",
                                                    mode="solver",
                                                    show_gui=is_gui,
                                                    version="3d",
                                                    precision="double",
                                                    processor_count=16,
                                                    cleanup_on_exit=False)
            solver.tui.file.read_case(mesh_path)
        run_sim(solver, v, area_ref, length_ref, res_tol, idx, iteration_dir, reynolds_is_iter=True)
        start_id += 1
        idx += 1
