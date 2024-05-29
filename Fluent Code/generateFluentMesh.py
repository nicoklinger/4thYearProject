import ansys.fluent.core as pyfluent

def generate_fluent_mesh(version, n_processor, iteration_dir, mesh_file_path, is_gui, is_mesh_conv=False,
                         disk_mesh_size=0.05):
    # Function that changes the mesh size of the disk

    # Start Meshing Session
    meshing_session = pyfluent.launch_fluent(product_version=version,
                                             mode="meshing",
                                             show_gui=is_gui,
                                             version="3d",
                                             precision="double",
                                             processor_count=n_processor,
                                             cleanup_on_exit=True)

    print("Fluent meshing session started\n")

    meshing_session.workflow.InitializeWorkflow(WorkflowType="Watertight Geometry")

    # Import Mesh File
    mesh_import = meshing_session.workflow.TaskObject["Import Geometry"]
    file_type = "Mesh"
    mesh_import.Arguments = {"FileFormat": file_type,
                             "ImportCadPreferences": {"CISeparation": "region"},
                             "MeshFileName": mesh_file_path}
    mesh_import.Execute()

    # Add Local Size to Disk
    add_loc_size = meshing_session.workflow.TaskObject['Add Local Sizing']
    if is_mesh_conv:
        name_size = "disk_size"
        name_body = "seedfaces"
        add_loc_size.Arguments = {"AddChild": "yes",
                                  "BOIControlName": name_size,
                                  "BOIFaceLabelList": [name_body],
                                  "BOISize": disk_mesh_size}
    else:
        add_loc_size.Arguments = {"AddChild": "no"}
    add_loc_size.AddChildAndUpdate()

    # Generate Surface Mesh
    surf_mesh = meshing_session.workflow.TaskObject['Generate the Surface Mesh']
    if is_mesh_conv:
        surf_mesh.Arguments = {"CFDSurfaceMeshControls": {"MaxSize": disk_mesh_size, "MinSize": disk_mesh_size,
                                                      "RemeshImportedMesh": "Assigned in Local Sizing"}}
    else:
        surf_mesh.Arguments = {"CFDSurfaceMeshControls": {"RemeshImportedMesh": "None"}}
    surf_mesh.Execute()

    # Describe Geometry
    describe_geo = meshing_session.workflow.TaskObject['Describe Geometry']
    describe_geo.UpdateChildTasks(SetupTypeChanged=False)
    describe_geo.Arguments = {"SetupType": "The geometry consists of both fluid and solid regions and/or voids"}
    describe_geo.UpdateChildTasks(SetupTypeChanged=True)
    describe_geo.Execute()

    # Update Boundaries and Regions
    update_boundaries = meshing_session.workflow.TaskObject['Update Boundaries']
    update_boundaries.Execute()
    update_regions = meshing_session.workflow.TaskObject['Update Regions']
##    update_regions.Arguments = {"OldRegionNameList": ["origin-seedfaces"],
##                                "OldRegionTypeList": ["solid"],
##                                "RegionNameList": ["origin-wall"],
##                                "RegionTypeList": ["fluid"]}
    update_regions.Execute()

    # Add Boundary Layers
    add_boundary_layers = meshing_session.workflow.TaskObject['Add Boundary Layers']
    add_boundary_layers.Arguments = {"FaceScope": {"GrowOn": "selected-zones"},
                                     "LocalPrismPreferences": {"Continuous": "Stair Step"},
                                     "ZoneSelectionList": ["seedfaces"]}
    add_boundary_layers.AddChildAndUpdate()

    # Generate Volume Mesh
    mesh_type = "tetrahedral"
    volume_mesh = meshing_session.workflow.TaskObject['Generate the Volume Mesh']
    volume_mesh.Arguments = {"VolumeFill": mesh_type}
    volume_mesh.Execute()

    # Check Mesh
    meshing_session.tui.mesh.check_mesh()

    # Save mesh file
    path = iteration_dir + '\\Mesh.msh.h5'
    meshing_session.tui.file.write_mesh(path)
    
    return meshing_session
