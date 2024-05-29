import cadquery as cq
import json
import os
from math import pi

def create_seed(t, r, h, spokes, circles, inside_r):
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
    result = result.union(cq.Workplane("XY").workplane(-h/2)
                          .circle(inside_r).extrude(h))
    bottom_face = result.faces("<Z").first()

    # Measure the area of the bottom face
    area = bottom_face.val().Area()

    return result, area

def create_assembly(t, r, h, spokes, circles, computer_os="Windows"):

    # Define domains dimensions
    h1 = 40 * r  # Big domain height (length) in mm
    r1 = 20 * r  # Big domain radius in mm

    h2 = 20 * r  # BOI height (length) in mm
    r2 = 10 * r  # BOI radius in mm

    # Generate seed to analyse
    seed, area = create_seed(t, r, h, spokes, circles)

    # Gerenate domains

    # Big domain
    cyl1 = cq.Workplane("front").workplane(-h / 2 - 10 * r)  # shift down workplane to have body symmetric around origin
    cyl1 = cyl1.circle(r1).extrude(h1)  # create and extrude circle

    # Mini domain (BoI)
    cyl2 = cq.Workplane("front").workplane(-h / 2 - 4 * r)  # shift down workplane to have body symmetric around origin
    cyl2 = cyl2.circle(r2).extrude(h2)  # create and extrude circle

    # Create and export assembly with all parts
    assy = cq.Assembly().add(cyl1, name="big_domain").add(cyl2, name="boi").add(seed, name="seed")
    AssyName = f"AssySeed_{h}h_{r}r_{t}t_{spokes}spokes_{circles}Circles".replace('.','')
    if computer_os=="Mac":
        FilePath = "Sims/" + AssyName + "/" + f"{AssyName}.step"
    else:
        FilePath = "Sims\\" + AssyName + "\\" + f"{AssyName}.step"

    if not os.path.isfile(FilePath):
        if computer_os == "Mac":
            os.makedirs(f"Sims/{AssyName}")
        else:
            os.makedirs(f"Sims\\{AssyName}")

        assy.save(f"{FilePath}")

        # Save data to JSON file stored in same folder as Assy
        json_data = {"surf_area":area,
                     "seed_radius":r,
                     "seed_height":h,
                     "spokes":spokes,
                     "spokes_thickness":t,
                     "circles":circles,
                     "big_domain_r":r1,
                     "big_domain_h":h1,
                     "boi_r":r2,
                     "boi_h":h2,
                     "porosity":(pi*r**2-area)/(pi*r**2)}
        if computer_os == "Mac":
            json_path = "Sims/" + AssyName + "/" + f"{AssyName}.json"
        else:
            json_path = "Sims\\" + AssyName + "\\" + f"{AssyName}.json"
        with open(json_path, 'w') as f:
            json.dump(json_data, f)
    else:
        print(f"File is already stored in Sims/{AssyName} ...")
    return AssyName