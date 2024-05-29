def run_sim(solver, v_inlet, area_ref, length_ref, res_tol, n_iterations, v_index, path_data, reynolds_is_iter=False):
    # Setup and Run a Sim

    # Change Working Directory
    new_dir = "chdir " + path_data
    solver.execute_tui(new_dir)

    # Laminar model
    solver.tui.define.models.viscous.laminar("yes")

    # Set Velocity Inlet
    velocity_inlet = solver.tui.define.boundary_conditions.set.velocity_inlet
    velocity_inlet("inlet", [], "vmag", "no", v_inlet, "quit")

    # Set No Shear Stress at Wall
    shear_x = 0
    shear_y = 0
    shear_z = 0
    solver.tui.define.boundary_conditions.wall("wall",
                                               "seedfaces-shadow",
                                               "no",
                                               "yes",
                                               "shear-bc-spec-shear",
                                               "no",
                                               shear_x,
                                               "no",
                                               shear_y,
                                               "no",
                                               shear_z)

    # Reference values
    solver.tui.report.reference_values.compute.velocity_inlet("inlet")
    solver.tui.report.reference_values.area(area_ref)
    solver.tui.report.reference_values.length(length_ref)
    solver.tui.report.reference_values.velocity(v_inlet)

    # Plane and line to extract data
    if v_index == 0:
        solver.tui.surface.plane_surface("pathlines", "yz-plane", "0")
        solver.tui.surface.line_surface("centre_line", "()", "()", "()", "()", "()", 5*length_ref)

    # Report Definitions
    name_report = "Cd"
    report_type = "drag"
    if v_index == 0:
        solver.tui.solve.report_definitions.add(name_report, report_type)
        solver.tui.solve.report_definitions.edit(name_report, "force-vector", 0, 0, 1)
        solver.tui.solve.report_definitions.edit(name_report, "thread-names", "seedfaces")
        solver.tui.solve.report_files.add(name_report)
    report_file_name = path_data + "/Cd_report_" + "v" + str(v_index) + ".csv"
    solver.tui.solve.report_files.edit(name_report, "file-name", report_file_name, "report-defs", name_report)

    # Residuals Convergece criteria
    solver.tui.solve.monitors.residual.convergence_criteria(res_tol, res_tol, res_tol, res_tol)

    # Number of iterations
    solver.tui.solve.set.number_of_iterations(n_iterations)

    # Solve problem
    solver.tui.solve.initialize.initialize_flow("yes")
    solver.tui.solve.iterate()

    # Export ASCII file with solution data
    sol_data_name = "Flow_data.csv"
    solver.tui.file.export.ascii(sol_data_name, "pathlines", "()", "no",
                                 "x-coordinate",
                                 "y-coordinate",
                                 "z-coordinate",
                                 "x-velocity",
                                 "y-velocity",
                                 "z-velocity",
                                 "velocity-magnitude",
                                 "pressure",
                                 "q",
                                 "no")

    # Save Fluent File
    solver.tui.file.write_case_data(path_data + "/Fluent_Sim")
    if not reynolds_is_iter:
        solver.exit()
        # solver.execute_tui("exit")
        print("Fluent session closed")

    return report_file_name

