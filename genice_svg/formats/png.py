# coding: utf-8
"""
GenIce format plugin to generate a PNG file.

Usage:
    % genice CS2 -r 3 3 3 -f png[shadow:bg=#f00] > CS2.png

Options:
    rotatex=30
    rotatey=30
    rotatez=30
    shadow         Draw shadows behind balls.
    bg=#f00        Specify the background color.
    H=0            Size of the hydrogen atom
    O=0.06
    HB=0.4
    OH=0.5
    width=0        (Pixel)
    height=0       (Pixel)
    encode=True    Encode into PNG or return as a bitmap.
"""


desc = { "ref": {},
         "brief": "PNG (Portable Network Graphics).",
         "usage": __doc__,
         }


import re
from math import sin, cos, pi
import numpy as np
from logging import getLogger

from genice_svg.render_png import Render

import genice_svg.formats.svg
class Format(genice_svg.formats.svg.Format):
    """
    Format into a PNG file.

    Options:
        rotatex=30
        rotatey=30
        rotatez=30
        polygon        Draw polygons instead of a ball and stick model.
        shadow=#8881   Draw shadows behind balls.
        bg=#f00        Specify the background color.
        O=0.06
        H=0            Size of the hydrogen atom (relative to that of oxygen)
        HB=0.4         Radius of HB relative to that of oxygem
        OH=0.5         Radius of OH colvalent bond relative to that of oxygem
        width=0        (Pixel)
        height=0       (Pixel)
        encode=True    Encode into PNG or return as a bitmap.
    """
    def __init__(self, **kwargs):
        logger = getLogger()
        super().__init__(**kwargs)
        self.poly     = False # unavailable for PNG
        self.arrows   = False # always false for png
        self.renderer = Render # png renderer
