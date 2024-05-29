from ansys.mechanical.core import launch_mechanical


def create_mesh(geometry_file_path, project_file_path, mesh_file_path,
                element_size_general, element_size_boi, element_size_seed):

    # geometry_file_path = path to .step
    # project_file_path = path to .mechdat
    # mesh_file_path = path to .msh
    # element_size_general, element_size_boi, element_size_seed = floats
    # ALL PATHS SHOULD BE BUILT WITH 4 \ TO SEPARATE FOLDERS

    print("Launching an Ansys Mechanical session to create the mesh ...\n")
    # Launch Mechanical Remote session
    mechanical = launch_mechanical(batch=True, cleanup_on_exit=False)
    print(mechanical)
    print('\n')

    # Import all necessary variables to Mechanical sesions
    mechanical.run_python_script(f"geometry_file_path = '{geometry_file_path}'")
    mechanical.run_python_script(f"project_file_path = '{project_file_path}'")
    mechanical.run_python_script(f"mesh_file_path = '{mesh_file_path}'")
    mechanical.run_python_script(f"element_size_general = {element_size_general}")
    mechanical.run_python_script(f"element_size_boi = {element_size_boi}")
    mechanical.run_python_script(f"element_size_seed = {element_size_seed}")

    print("All paths successfully imported\n")

    mechanical.run_python_script(
        """
# GEOMETRY IMPORT
geometry_import_group_11 = Model.GeometryImportGroup
geometry_import_12 = geometry_import_group_11.AddGeometryImport()
geometry_import_12.Import(geometry_file_path)
        """
    )
    print("Geometry imported in Mechanical session successfully")
    mechanical .run_python_script(
        """
# ADD FIRST NAMED SELECTION
named_selection_inlet = Model.AddNamedSelection()

selection_inlet = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities) # Select the face
selection_inlet.Ids = [14]

named_selection_inlet.Location = selection_inlet
named_selection_inlet.Name = r"Inlet"

# ADD SECOND NAMED SELECTION
named_selection_outlet = Model.AddNamedSelection()

selection_outlet = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities) # Select the face
selection_outlet.Ids = [15]

named_selection_outlet.Location = selection_outlet
named_selection_outlet.Name = r"Outlet"

# ADD THIRD NAMED SELECTION
named_selection_wall = Model.AddNamedSelection()

selection_wall = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities) # Select the face
selection_wall.Ids = [13]

named_selection_wall.Location = selection_wall
named_selection_wall.Name = r"Wall"

# SELECT SEED BODY FACES
seed_body = DataModel.GetObjectsByType(DataModelObjectCategory.Body)[2]
list_of_faces = seed_body.GetGeoBody().Faces
id_of_faces = []
for i in list_of_faces:
    id_of_faces.append(i.Id)

# ADD NAMED SELECTION FOR SEED BODY FACES
named_selection_seed = Model.AddNamedSelection()

selection_seed = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities) # Select the face
selection_seed.Ids = id_of_faces

named_selection_seed.Location = selection_seed
named_selection_seed.Name = r"SeedFaces"

        """
    )
    print("All named selections added\n")
    mechanical.run_python_script(
        """
# GET ID OF ALL BODIES
seed_body_id = seed_body.GetGeoBody().Id
big_domain_body_id = DataModel.GetObjectsByType(DataModelObjectCategory.Body)[0].GetGeoBody().Id
boi_body_id = DataModel.GetObjectsByType(DataModelObjectCategory.Body)[1].GetGeoBody().Id

# CREATE MESH
mesh= Model.Mesh

# SET GENERAL ELEMENT DIMENSION
mesh.PhysicsPreference = MeshPhysicsPreferenceType.CFD      # Sets mesh type to CFD
mesh.ElementSize = Quantity(element_size_general, "m")
mesh.MaximumSize = Quantity(element_size_general, "m")

# SET DOMAIN SIZING

# SELECT BIG DOMAIN
sizing_domain = mesh.AddSizing()
selection_big_domain = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
selection_big_domain.Ids = [big_domain_body_id]

sizing_domain.Location = selection_big_domain

# SELECT BOI
sizing_domain.Type = SizingType.BodyOfInfluence
selection_boi = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
selection_boi.Ids = [boi_body_id]
sizing_domain.BodyOfInfluence = selection_boi

# DOMAIN SIZING
sizing_domain.ElementSize = Quantity(element_size_boi, "m")

# SET SEED BODY SIZING
sizing_seed = mesh.AddSizing()
sizing_seed.Location = selection_seed

sizing_seed.ElementSize = Quantity(element_size_seed, "m")

# SET TETRAHEDRONS METHOD
method = mesh.AddAutomaticMethod()
method.Location = selection_big_domain
method.Method = MethodType.AllTriAllTet

# GENERATE MESH
mesh.GenerateMesh()
        """
    )
    print("Mesh generated with all requested features\n")
    mechanical.run_python_script(
        """
# EXPORT PROJECT FILE
ExtAPI.DataModel.Project.Save(project_file_path)
    """
    )
    print(f"Project saved successfully at {project_file_path}\n")
    mechanical.run_python_script(
        """
# EXPORT MESH FILE
ExtAPI.DataModel.Project.Model.Mesh.InternalObject.WriteFluentInputFile(mesh_file_path)
        """
    )
    print(f"Mesh saved successfully at {mesh_file_path}\n")

    mechanical.exit()

    print("Mechanical instance closed ... \n")