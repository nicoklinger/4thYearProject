def run_sim(solver, v_inlet, area_ref, length_ref, res_tol, v_index, path_data, reynolds_is_iter=False):
    # Setup and Run a Sim

    # Change Working Directory
    new_dir = "chdir " + path_data
    solver.execute_tui(new_dir)

    # Laminar transient model
    solver.tui.define.models.viscous.laminar("yes")
    solver.tui.define.models.unsteady_2nd_order_bounded("yes")
    solver.tui.solve.set.p_v_coupling("21")
    time_step = "0.01"
    solver.tui.solve.set.transient_controls.time_step_size(time_step)
    n_iter = "1500"
    n_iter_per_step = "10"
    solver.tui.solve.set.transient_controls.number_of_time_steps(n_iter)
    solver.tui.solve.set.transient_controls.max_iterations_per_time_step(n_iter_per_step)

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

    name_report = "Cl_x"
    report_type = "lift"
    if v_index == 0:
        solver.tui.solve.report_definitions.add(name_report, report_type)
        solver.tui.solve.report_definitions.edit(name_report, "force-vector", 1, 0, 0)
        solver.tui.solve.report_definitions.edit(name_report, "thread-names", "seedfaces")
        solver.tui.solve.report_files.add(name_report)
    report_file_name = path_data + "/Cl_x_report_" + "v" + str(v_index) + ".csv"
    solver.tui.solve.report_files.edit(name_report, "file-name", report_file_name, "report-defs", name_report)

    name_report = "Cl_y"
    report_type = "lift"
    if v_index == 0:
        solver.tui.solve.report_definitions.add(name_report, report_type)
        solver.tui.solve.report_definitions.edit(name_report, "force-vector", 0, 1, 0)
        solver.tui.solve.report_definitions.edit(name_report, "thread-names", "seedfaces")
        solver.tui.solve.report_files.add(name_report)
    report_file_name = path_data + "/Cl_y_report_" + "v" + str(v_index) + ".csv"
    solver.tui.solve.report_files.edit(name_report, "file-name", report_file_name, "report-defs", name_report)

    name_report = "Cm_x"
    report_type = "moment"
    if v_index == 0:
        solver.tui.solve.report_definitions.add(name_report, report_type)
        solver.tui.solve.report_definitions.edit(name_report, "mom-axis", 1, 0, 0)
        solver.tui.solve.report_definitions.edit(name_report, "thread-names", "seedfaces")
        solver.tui.solve.report_files.add(name_report)
    report_file_name = path_data + "/Cm_x_report_" + "v" + str(v_index) + ".csv"
    solver.tui.solve.report_files.edit(name_report, "file-name", report_file_name, "report-defs", name_report)

    name_report = "Cm_y"
    report_type = "moment"
    if v_index == 0:
        solver.tui.solve.report_definitions.add(name_report, report_type)
        solver.tui.solve.report_definitions.edit(name_report, "mom-axis", 0, 1, 0)
        solver.tui.solve.report_definitions.edit(name_report, "thread-names", "seedfaces")
        solver.tui.solve.report_files.add(name_report)
    report_file_name = path_data + "/Cm_y_report_" + "v" + str(v_index) + ".csv"
    solver.tui.solve.report_files.edit(name_report, "file-name", report_file_name, "report-defs", name_report)

    name_report = "Cm_z"
    report_type = "moment"
    if v_index == 0:
        solver.tui.solve.report_definitions.add(name_report, report_type)
        solver.tui.solve.report_definitions.edit(name_report, "mom-axis", 0, 0, 1)
        solver.tui.solve.report_definitions.edit(name_report, "thread-names", "seedfaces")
        solver.tui.solve.report_files.add(name_report)
    report_file_name = path_data + "/Cm_z_report_" + "v" + str(v_index) + ".csv"
    solver.tui.solve.report_files.edit(name_report, "file-name", report_file_name, "report-defs", name_report)

    # Residuals Convergece criteria
    solver.tui.solve.monitors.residual.convergence_criteria(res_tol, res_tol, res_tol, res_tol)

    # Solve problem
    solver.tui.solve.initialize.initialize_flow("yes")
    solver.tui.solve.dual_time_iterate(n_iter, n_iter_per_step)

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

        print("Fluent session closed")

    return report_file_name
