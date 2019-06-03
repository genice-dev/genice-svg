# coding: utf-8
"""
PNG, derived from SVG format rev. 2
"""


from math import pi, cos, sin

import numpy as np

from genice_svg import hooks
from genice_svg.render_svg import Render

    

 
            
def Normal(vs):
    """
    Normal vector (not normalized)
    """
    n = np.zeros(3)
    for i in range(vs.shape[0]):
        n += np.cross(vs[i-1], vs[i])
    return n


sun = np.array([-1.,-1.,2.])
sun /= np.linalg.norm(sun)



        
# set of hue and saturation
hue_sat = {3:(60., 0.8),
           4:(120, 0.8), # yellow-green
           5:(180, 0.5), # skyblue
           6:(240, 0.5), # blue
           7:(300, 0.8), #
           8:(350, 0.5)} # red-purple



def hook0(lattice, arg):
    lattice.logger.info("Hook0: ArgParser.")
    lattice.renderer = Render
    lattice.poly     = False
    lattice.shadow   = None
    lattice.oxygen   = 0.06 # absolute radius in nm
    lattice.HB       = 0.4  # radius relative to the oxygen
    lattice.OH       = 0.5  # radius relative to the oxygen
    lattice.hydrogen = 0    # radius relative to the oxygen
    lattice.arrows   = False
    lattice.proj = np.array([[1., 0, 0], [0, 1, 0], [0, 0, 1]])
    if arg == "":
        pass
        #This is default.  No reshaping applied.
    else:
        args = arg.split(":")
        for a in args:
            if a.find("=") >= 0:
                key, value = a.split("=")
                lattice.logger.info("Option with arguments: {0} := {1}".format(key,value))
                if key == "rotmat":
                    value = re.search(r"\[([-0-9,.]+)\]", value).group(1)
                    lattice.proj = np.array([float(x) for x in value.split(",")]).reshape(3,3)
                elif key == "rotatex":
                    value = float(value)*pi/180
                    cosx = cos(value)
                    sinx = sin(value)
                    R = np.array([[1, 0, 0], [0, cosx, sinx], [0,-sinx, cosx]])
                    lattice.proj = np.dot(lattice.proj, R)
                elif key == "rotatey":
                    value = float(value)*pi/180
                    cosx = cos(value)
                    sinx = sin(value)
                    R = np.array([[cosx, 0, -sinx], [0, 1, 0], [sinx, 0, cosx]])
                    lattice.proj = np.dot(lattice.proj, R)
                elif key == "rotatez":
                    value = float(value)*pi/180
                    cosx = cos(value)
                    sinx = sin(value)
                    R = np.array([[cosx, sinx, 0], [-sinx, cosx, 0], [0, 0, 1]])
                    lattice.proj = np.dot(lattice.proj, R)
                elif key == "shadow":
                    lattice.shadow = value
                elif key == "H":
                    lattice.hydrogen = float(value)
                elif key == "HB":
                    lattice.HB = float(value)
                elif key == "O":
                    lattice.oxygen = float(value)
                elif key == "OH":
                    lattice.OH = float(value)
            else:
                lattice.logger.info("Flags: {0}".format(a))
                if a == "shadow":
                    lattice.shadow = "#8881"
                elif a == "polygon":
                    lattice.poly = True
                elif a == "H":
                    lattice.hydrogen = 0.6
                    lattice.HB = 0.2
                elif a == "OH":
                    lattice.OH = 0.5
                elif a == "arrows":
                    lattice.arrows = True
                else:
                    assert False, "Wrong options."
    lattice.logger.info("Hook0: end.")




hooks = {0:hook0, 2:hooks.hook2, 6:hooks.hook6}

