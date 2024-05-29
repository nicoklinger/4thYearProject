from CreateGeometryBoolean import create_assembly

############################################
## Modify the computer OS in the function ##
########## default = Windows ###############
############################################

# This script creates seed from scratch!!!

r = 22/2      # Seed diameter in mm
h = 0.5     # Seed high in mm
t = 0.3    # Thickness of spokes in mm

spokes = 82     # Number of spokes in the seed
circles = 0     # Number of concentric circles

inside_r = 11/2
outside_r = 44/2
angle = 15

create_assembly(t=t, r=r, h=h, spokes=spokes, circles=circles, inside_r=inside_r, outside_r=outside_r, rotation_angle=angle)
