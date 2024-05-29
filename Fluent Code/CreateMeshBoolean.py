from ansys.mechanical.core import launch_mechanical
import json
import os.path

def create_mesh(geometry_file_path, project_file_path, mesh_file_path,
                element_size_general, element_size_boi, element_size_seed, json_file_path,
                save_element_number=True):

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

    with open(json_file_path) as f:
        geom_data = json.load(f)

    h = geom_data['seed_height']
    r = geom_data['seed_radius']

##    d1 = '%.5f' % (-h / 2 - 10 * r)
##    d11= (-h / 2 - 10 * r)
##    d2 = '%.5f' % (geom_data['big_domain_h'] - abs(d11))
##    d3 = '%.5f' % (geom_data['big_domain_h']/2 - abs(d11))
    d1 = round(geom_data['big_dom_inlet_face'], 3)
    d2 = round(geom_data['big_dom_outlet_face'], 3)
    d3 = round(geom_data['big_dom_centre'], 3)
    print(d1, d2, d3)

    # Import all necessary variables to Mechanical sesions
    mechanical.run_python_script(f"geometry_file_path = '{geometry_file_path}'")
    mechanical.run_python_script(f"project_file_path = '{project_file_path}'")
    mechanical.run_python_script(f"mesh_file_path = '{mesh_file_path}'")
    mechanical.run_python_script(f"element_size_general = {element_size_general}")
    mechanical.run_python_script(f"element_size_boi = {element_size_boi}")
    mechanical.run_python_script(f"element_size_seed = {element_size_seed}")
    mechanical.run_python_script(f"d1 = {d1}")
    mechanical.run_python_script(f"d2 = {d2}")
    mechanical.run_python_script(f"d3 = {d3}")


    print("All paths and parameters successfully imported ...\n")

    mechanical.run_python_script(
        """
# GEOMETRY IMPORT
geometry_import_group_11 = Model.GeometryImportGroup
geometry_import_12 = geometry_import_group_11.AddGeometryImport()
geometry_import_12.Import(geometry_file_path)
        """
    )
    print("Geometry imported in Mechanical session successfully\n")
    output = mechanical.run_python_script(
        """
# SELECT DOMAIN BODY FACES
domain_body = DataModel.GetObjectsByType(DataModelObjectCategory.Body)[0]
list_of_faces = domain_body.GetGeoBody().Faces
id_of_faces = []
area_of_faces = []
centroid_of_faces = []

for i in list_of_faces:
    id_of_faces.append(i.Id)
    centroid_of_faces.append(round(i.Centroid[2],3))
    """)
    mechanical.run_python_script(
        """
inlet_face_id = id_of_faces[centroid_of_faces.index((d1))]
outlet_face_id = id_of_faces[centroid_of_faces.index((d2))]
wall_face_id = id_of_faces[centroid_of_faces.index((d3))]

id_of_faces.remove(inlet_face_id)
id_of_faces.remove(outlet_face_id)
id_of_faces.remove(wall_face_id)
 
# ADD FIRST NAMED SELECTION
named_selection_inlet = Model.AddNamedSelection()

selection_inlet = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities) # Select the face
selection_inlet.Ids = [inlet_face_id]

named_selection_inlet.Location = selection_inlet
named_selection_inlet.Name = r"Inlet"

# ADD SECOND NAMED SELECTION
named_selection_outlet = Model.AddNamedSelection()

selection_outlet = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities) # Select the face
selection_outlet.Ids = [outlet_face_id]

named_selection_outlet.Location = selection_outlet
named_selection_outlet.Name = r"Outlet"

# ADD THIRD NAMED SELECTION
named_selection_wall = Model.AddNamedSelection()

selection_wall = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities) # Select the face
selection_wall.Ids = [wall_face_id]

named_selection_wall.Location = selection_wall
named_selection_wall.Name = r"Wall"


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
    connection = mechanical.run_python_script(
        """
try:
    Model.Connections.Children[0].Delete()
    output="Connection deleted"
    output
except:
    output = "no connections to delete"
    output
        """
    )
    print(connection)
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
    elements_number = mechanical.run_python_script(
        """
def return_elements_number(mesh):
    elements_number = mesh.Elements
    return elements_number
return_elements_number(mesh)
        """
    )
    print(f"The mesh has {elements_number} elements")
    mechanical.exit()

    print("Mechanical instance closed ... \n")

    elements_file_path = os.path.dirname(mesh_file_path.replace('\\\\\\\\', '\\'))

    # Save elements number txt
    if save_element_number:
        with open(f'{elements_file_path}\\elements_number.txt','w') as f:
            f.write(elements_number)

    # Save mesh features txt
    with open(f'{elements_file_path}\\mesh_features.txt','w') as f:
        f.write(f"{element_size_general}, {element_size_boi}, {element_size_seed}")

    return elements_number
