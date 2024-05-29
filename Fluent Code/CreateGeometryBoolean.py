import cadquery as cq
import json
import os
from math import pi, sin

def create_seed(t, r, h, spokes, circles, inside_r, outside_r):
    # Creates 1st spoke
    result = cq.Workplane("XY").workplane(-h/2)
    result = result.box(t, r, h, (True, False, False))

    # Creates all spokes, rotates and merges
    i = 1
    while i <= (spokes-1):
        result = result.union(
            cq.Workplane("XY").workplane(-h/2).center(-t/2,0).box(t, r, h, (False, False, False)).
                rotate((0, 0, 0), (0, 0, 1),  i*(360/(spokes)))
            )
        i += 1

    # Creates all circles and merges to previous body
    i = 1
    while i <= circles:
        result = result.union(cq.Workplane("XY").workplane(-h/2)
                      .circle(i*(r)/circles+t/2).extrude(h)
                      .faces(">Z").workplane().hole(i*(r*2)/circles-t))
        i += 1
    # Add inside circle
    result = result.union(cq.Workplane("XY").workplane(-h/2)
                          .circle(inside_r).extrude(h))

    # Add outside circle
    result = result.union(cq.Workplane("XY").workplane(-h / 2)
                          .circle(outside_r).extrude(h)
                          .faces(">Z").workplane().hole(r * 2))

    bottom_face = result.faces("<Z").first()

    # Measure the area of the bottom face
    area = bottom_face.val().Area()

    return result, area

def create_assembly(t, r, h, inside_r, outside_r, spokes=None, circles=None, area=None, spec_design=None, rotation_angle=None,
                    computer_os="Windows"):

    cur_dir = os.getcwd()

    # Define domains dimensions
    h1 = 10 * outside_r  # Big domain height (length) in mm
    r1 = 7 * outside_r  # Big domain radius in mm

    h2 = 5 * outside_r  # BOI height (length) in mm
    r2 = 2.5 * outside_r  # BOI radius in mm

    if spec_design == None:
        # Generate seed to analyse
        print("No manually created design specified, generating a seed design file using the input values \n")
        # Checks that all input variables were added, if not error is printed and function is stopped
        if area != None:
            print("ERROR: A value for the surfaces area was specified, please delete it from the input arguments"
                  "\n \n Aborting ...")
            return
        elif spokes == None:
            print("ERROR: A value for the spokes was not specified, please add it in the input arguments"
                  "\n \n Aborting ...")
            return
        elif circles == None:
            print("ERROR: A value for the circles was not specified, please add it in the input arguments"
                  "\n \n Aborting ...")
            return

        # If all input variables are present, create the seed
        seed, area = create_seed(t, r, h, spokes, circles, inside_r, outside_r)
    else:
        # Use specified design to create assy file
        print(f"Design {spec_design} was specified. Creating an Assy file for it")
        if area == None:
            print("ERROR: You need to specify a value for the surface area as input. \n Use area = number input argument"
                  "\n \n Aborting ...")
            return
        if spokes != None or circles != None:
            print("WARNING: a number of Circles or Spokes was specified, disregarding them and opening specified file"
                  "\n \n Aborting ...")

        # Open desired step file in cadquery
        path_to_my_design = f"{cur_dir}\\ManualGeometries\\{spec_design}.step"

        # Change \\ to / if OS is Mac
        if computer_os == "Mac":
            path_to_my_design.replace('\\','/')

        if not os.path.isfile(path_to_my_design):
            print("Could not find the specified file in ManualGeometries folder. \n \n Aborting...")
            return
        # If geometry file is found, open it in CQ
        seed = cq.importers.importStep(path_to_my_design)

    if not rotation_angle == None:
        seed = seed.rotate((0,0,0), (1,0,0), rotation_angle)
    # Gerenate domains

    # Big domain
    


    # Mini domain (BoI)
    if rotation_angle==None:
         boi_ext = round(-3 * h, 5)
         big_dom_ext = round(-h / 2 - h1/4, 5)
    else:
        boi_ext = round(-3 * h - outside_r*sin(rotation_angle*pi/180), 5)
        big_dom_ext = round(-h / 2 - h1/4 - outside_r*sin(rotation_angle*pi/180), 5)

    cyl1 = cq.Workplane("front").workplane(big_dom_ext)  # shift down workplane to have body symmetric around origin
    cyl1 = cyl1.circle(r1).extrude(h1)  # create and extrude circle

    cyl1 = cyl1.cut(seed)   # Subtract boolean
    
    cyl2 = cq.Workplane("front").workplane(boi_ext)  # shift down workplane to have body symmetric around origin
    cyl2 = cyl2.circle(r2).extrude(h2)  # create and extrude circle

    # Create and export assembly with all parts
    assy = cq.Assembly().add(cyl1, name="big_domain").add(cyl2, name="boi")

    if spec_design == None and rotation_angle == None:
        AssyName = f"AssySeed_{h}h_{r}r_{t}t_{spokes}spokes_{circles}Circles_{inside_r}InsideR_{outside_r}OutsideR".replace('.','')
    elif not spec_design == None and rotation_angle == None:
        AssyName = f"Assy_{spec_design}"
    elif spec_design == None and not rotation_angle == None:
        AssyName = f"AssySeed_{h}h_{r}r_{t}t_{spokes}spokes_{circles}Circles_{inside_r}InsideR_{outside_r}OutsideR_{rotation_angle}degrees".replace('.', '')
    elif not spec_design == None and not rotation_angle == None:
        AssyName = f"Assy_{spec_design}_{rotation_angle}degrees"

    if computer_os=="Mac":
        FilePath = "Sims/" + AssyName + "/" + f"{AssyName}.step"
    else:
        FilePath = "Sims\\" + AssyName + "\\" + f"{AssyName}.step"

    if os.path.isfile(FilePath):
        print("A file with the same name is already present. Is the file a duplicate? \n \n Aborting ...")
        return
    else:
        if computer_os == "Mac" and not not os.path.isdir(f"Sims/{AssyName}"):
            os.makedirs(f"Sims/{AssyName}")
        elif not os.path.isdir(f"Sims/{AssyName}"):
            os.makedirs(f"Sims\\{AssyName}")

        assy.save(f"{FilePath}")

        # Save data to JSON file stored in same folder as Assy
        json_data = {"surf_area":area,
                     "seed_radius":r,
		     "outside_r":outside_r,
                     "seed_height":h,
                     "spokes":int(spokes),
                     "spokes_thickness":t,
                     "circles":int(circles),
                     "big_domain_r":r1,
                     "big_domain_h":h1,
                     "boi_r":r2,
                     "boi_h":h2,
                     "porosity":(pi*r**2-area)/(pi*r**2),
                     "boleean":True,
                     "big_dom_inlet_face":big_dom_ext,
                     "big_dom_outlet_face":h1+big_dom_ext, 
                     "big_dom_centre":h1/2+big_dom_ext}

        if computer_os == "Mac":
            json_path = "Sims/" + AssyName + "/" + f"{AssyName}.json"
        else:
            json_path = "Sims\\" + AssyName + "\\" + f"{AssyName}.json"
        with open(json_path, 'w') as f:
            json.dump(json_data, f)

    return AssyName
