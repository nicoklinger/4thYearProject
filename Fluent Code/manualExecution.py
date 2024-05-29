from CreateGeometryBoolean import create_assembly
from CreateMeshBoolean import create_mesh
from runSim import run_sim
import cadquery as cq
import os
import json
import ansys.fluent.core as pyfluent
from math import pi

# NOTE: a folder with the name EXACTLY as the step file to be tested needs to be created into ManualSims

# If you need to make a new file - needs to be True if it is the first time testing that file.
make_file_with_my_design = True

# If you don'r want to run the meshing and the sim, set to False
run_sim = False

step_file_name = "Validation10AR"   # do not write .step
cur_dir = os.getcwd()
folder = f"{cur_dir}\\ManualSims\\{step_file_name}"

# h, r and area MUST BE CORRECT OTHERWISE THE WORFLOW WON'T WORK CORRECTLY
# (even if no error is returned, output data will be wrong)

r = 50/2                   # dimensions in mm
h = 2.5
area = 1963.495          # mm^2
spokes = 0              # for the following  3 parameters put at least a number, or FALSE
t = 0.25
circles = 0

element_size_general = 0.1
element_size_boi = 0.01
element_size_seed = 0.0001

# Parameters for simulation:
v_inlet = 0.5               # m/s
res_tol = 1e-6
n_iterations = 50

if make_file_with_my_design:
    path_to_my_design = f"{folder}\\{step_file_name}.step"
    file1 = cq.importers.importStep(path_to_my_design)

    # Define domains dimensions
    h1 = 10 * r  # Big domain height (length) in mm
    r1 = 7 * r  # Big domain radius in mm

    h2 = 5 * r  # BOI height (length) in mm
    r2 = 2.5 * r  # BOI radius in mm

    boi_ext = round(-3 * h, 5)
    big_dom_ext = round(-h / 2 - h1/4, 5)

    # Big domain
    cyl1 = cq.Workplane("front").workplane(big_dom_ext)  # shift down workplane to have body symmetric around origin
    cyl1 = cyl1.circle(r1).extrude(h1)  # create and extrude circle

    cyl1 = cyl1.cut(file1)  # Subtract boolean

    # Mini domain (BoI)
    cyl2 = cq.Workplane("front").workplane(boi_ext)  # shift down workplane to have body symmetric around origin
    cyl2 = cyl2.circle(r2).extrude(h2)  # create and extrude circle

    # Create and export assembly with all parts
    assy = cq.Assembly().add(cyl1, name="big_domain").add(cyl2, name="boi")
    AssyName = f"Assy{step_file_name}.step"
    assy.save(f"{folder}\\{AssyName}")

    json_path = path_to_my_design.replace('.step','.json')
    json_data = {"surf_area": area,
                 "seed_radius": r,
                 "seed_height": h,
                 "spokes": spokes,
                 "spokes_thickness": t,
                 "circles": circles,
                 "big_domain_r": r1,
                 "big_domain_h": h1,
                 "boi_r": r2,
                 "boi_h": h2,
                 "porosity": (pi * r ** 2 - area) / (pi * r ** 2),
                 "boleean": True,
                 "big_dom_inlet_face":big_dom_ext,
                 "big_dom_outlet_face":h1+big_dom_ext, 
                 "big_dom_centre":h1/2+big_dom_ext}
    
    with open(json_path, 'w') as f:
        json.dump(json_data, f)
else:
    path_to_my_design = f"{folder}\\{step_file_name}.step"
    json_path = f"{folder}\\{step_file_name}.json"

if run_sim:
    geometry_file_path = (folder + "\\Assy" + step_file_name + ".step").replace('\\','\\\\')
    project_file_path = path_to_my_design.replace('\\','\\\\\\\\').replace('.step','.mechdat')
    mesh_file_path = path_to_my_design.replace('\\','\\\\\\\\').replace('.step','.msh')

    print(geometry_file_path)

    create_mesh(geometry_file_path, project_file_path, mesh_file_path,
                    element_size_general, element_size_boi, element_size_seed, json_path)

    solver = pyfluent.launch_fluent(product_version="23.1.0",
                                    mode="solver",
                                    show_gui=True,
                                    version="3d",
                                    precision="double",
                                    processor_count=8,
                                    cleanup_on_exit=False)
    solver.tui.file.read_case(mesh_file_path.replace('\\\\\\\\','\\'))


    area_ref = area / 10**6
    length_ref = r * 2 / 1000
    v_index = 0

    run_sim(solver, v_inlet, area_ref, length_ref, res_tol, n_iterations, v_index, folder)

