# coding: utf-8
"""
GenIce format plugin to generate a PNG file.

Usage:
    % genice CS2 -r 3 3 3 -f svg[rotatex=30:shadow] > CS2.svg
	
Options:
    rotatex=30
    rotatey=30
    rotatez=30
    polygon        Draw polygons instead of a ball and stick model.
    shadow         Draw shadows behind balls.
    bg=#f00        Specify the background color.
    H=0            Size of the hydrogen atom
    O=0.06
    HB=0.4
    OH=0.5
    width=0        (Pixel)
    height=0       (Pixel)
"""

desc = { "ref": {},
         "brief": "SVG (Standard Vector Graphics).",
         "usage": __doc__,
         }



import re
from math import pi, cos, sin
from logging import getLogger

import numpy as np

from genice_svg import hooks
from genice_svg.render_svg import Render
from genice_svg.hooks import options

    

 
            
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
    logger = getLogger()
    logger.info("Hook0: ArgParser.")
    options.renderer = Render
    options.poly     = False
    options.shadow   = None
    options.oxygen   = 0.06 # absolute radius in nm
    options.HB       = 0.4  # radius relative to the oxygen
    options.OH       = 0.5  # radius relative to the oxygen
    options.hydrogen = 0    # radius relative to the oxygen
    options.arrows   = False
    options.bgcolor  = None
    options.proj = np.array([[1., 0, 0], [0, 1, 0], [0, 0, 1]])
    options.width    = 0
    options.height   = 0
    if arg == "":
        pass
        #This is default.  No reshaping applied.
    else:
        args = arg.split(":")
        for a in args:
            if a.find("=") >= 0:
                key, value = a.split("=")
                logger.info("  Option with arguments: {0} := {1}".format(key,value))
                if key == "rotmat":
                    value = re.search(r"\[([-0-9,.]+)\]", value).group(1)
                    options.proj = np.array([float(x) for x in value.split(",")]).reshape(3,3)
                elif key == "rotatex":
                    value = float(value)*pi/180
                    cosx = cos(value)
                    sinx = sin(value)
                    R = np.array([[1, 0, 0], [0, cosx, sinx], [0,-sinx, cosx]])
                    options.proj = np.dot(options.proj, R)
                elif key == "rotatey":
                    value = float(value)*pi/180
                    cosx = cos(value)
                    sinx = sin(value)
                    R = np.array([[cosx, 0, -sinx], [0, 1, 0], [sinx, 0, cosx]])
                    options.proj = np.dot(options.proj, R)
                elif key == "rotatez":
                    value = float(value)*pi/180
                    cosx = cos(value)
                    sinx = sin(value)
                    R = np.array([[cosx, sinx, 0], [-sinx, cosx, 0], [0, 0, 1]])
                    options.proj = np.dot(options.proj, R)
                elif key == "shadow":
                    options.shadow = value
                elif key == "H":
                    options.hydrogen = float(value)
                elif key == "HB":
                    options.HB = float(value)
                elif key == "O":
                    options.oxygen = float(value)
                elif key == "OH":
                    options.OH = float(value)
                elif key == "bg":
                    options.bgcolor = value
                elif key == "width":
                    options.width = int(value)
                elif key == "height":
                    options.height = int(value)
            else:
                logger.info("  Flags: {0}".format(a))
                if a == "shadow":
                    options.shadow = "#8881"
                elif a == "polygon":
                    options.poly = True
                elif a == "H":
                    options.hydrogen = 0.6
                    options.HB = 0.2
                elif a == "OH":
                    options.OH = 0.5
                elif a == "arrows":
                    options.arrows = True
                else:
                    assert False, "  Wrong options."
    logger.info("Hook0: end.")




hooks = {0:hook0, 2:hooks.hook2, 6:hooks.hook6}

