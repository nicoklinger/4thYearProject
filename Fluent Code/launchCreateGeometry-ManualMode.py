from CreateGeometryBoolean import create_assembly

############################################
## Modify the computer OS in the function ##
########## default = Windows ###############
############################################

# This script creates seed from scratch!!!

r = 10      # Seed diameter in mm
h = 0.5     # Seed high in mm
t = 10000    # Thickness of spokes in mm        this design has no spokes, put a large value for mesh specs (later use)
area = 314.159  # Area in mm^2

name_of_file = "ImperviousDisk"     # Name of file, MUST BE IN ManualGeometries folder

AssyName = create_assembly(t=t, r=r, h=h, area=area, spec_design=name_of_file)
print(f"Assy name is {AssyName}")