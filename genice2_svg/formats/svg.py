# coding: utf-8
"""
GenIce format plugin to generate a SVG file.

Usage:
    % genice CS2 -r 3 3 3 -f svg[rotatex=30:shadow] > CS2.svg

Options:
    rotatex=30
    rotatey=30
    rotatez=30
    polygon        Draw polygons instead of a ball and stick model.
    arrows         Draw the hydrogen bonds with arrows.
    shadow=#8881   Draw shadows behind balls.
    bg=#f00        Specify the background color.
    O=0.06
    H=0            Size of the hydrogen atom (relative to that of oxygen)
    HB=0.4         Radius of HB relative to that of oxygem
    OH=0.5         Radius of OH colvalent bond relative to that of oxygem
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
from collections import defaultdict

import numpy as np
import networkx as nx
from cycless.cycles import cycles_iter

from genice2_svg.render_svg import Render
import genice2.formats
from genice2.decorators import timeit, banner
from genice2.molecules  import serialize


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


def clip_cyl(v1, r1, v2, r2, rb):
    r1c = (r1**2 - rb**2)**0.5
    r2c = (r2**2 - rb**2)**0.5
    dv = v2 - v1
    Lv = np.linalg.norm(dv)
    if Lv < r1+r2:
        return None
    newv1 = v1 + dv*r1c/Lv
    newv2 = v2 - dv*r2c/Lv
    c = (newv1+newv2)/2
    d = c-newv2
    return [c, "L2", d]



def draw_cell(prims, cellmat, origin=np.zeros(3)):
    for a in (0., 1.):
        for b in (0., 1.):
            v0 = np.array([0., a, b]+origin)
            v1 = np.array([1., a, b]+origin)
            mid = (v0+v1)/2
            prims.append([np.dot(mid, cellmat),
                          "L",
                          np.dot(v0,  cellmat),
                          np.dot(v1,  cellmat), 0, {}])
            v0 = np.array([b, 0., a]+origin)
            v1 = np.array([b, 1., a]+origin)
            mid = (v0+v1)/2
            prims.append([np.dot(mid, cellmat),
                          "L",
                          np.dot(v0,  cellmat),
                          np.dot(v1,  cellmat), 0, {}])
            v0 = np.array([a, b, 0.]+origin)
            v1 = np.array([a, b, 1.]+origin)
            mid = (v0+v1)/2
            prims.append([np.dot(mid, cellmat),
                          "L",
                          np.dot(v0,  cellmat),
                          np.dot(v1,  cellmat), 0, {}])
    corners = []
    for x in (np.zeros(3), cellmat[0]):
        for y in (np.zeros(3), cellmat[1]):
            for z in (np.zeros(3), cellmat[2]):
                corners.append(x+y+z+origin)
    corners = np.array(corners)
    return np.min(corners[:,0]), np.max(corners[:,0]), np.min(corners[:,1]), np.max(corners[:,1])


class Format(genice2.formats.Format):
    """
    Format an ice structure into a SVG file.

    Options:
        rotatex=30
        rotatey=30
        rotatez=30
        polygon=True   Draw polygons instead of a ball and stick model.
        arrows=True    Draw the hydrogen bonds with arrows.
        shadow="#8881" Draw shadows behind balls with the specified color.
        shadow=True    Draw shadows behind balls with the default color.
        bg="#f00"      Specify the background color.
        O=0.06
        H=0            Size of the hydrogen atom (relative to that of oxygen)
        HB=0.4         Radius of HB relative to that of oxygem
        OH=0.5         Radius of OH colvalent bond relative to that of oxygem
        width=0        (Pixel)
        height=0       (Pixel)
    """
    def hooks(self):
        return {2:self.Hook2, 6:self.Hook6}

    @timeit
    @banner
    def __init__(self, **kwargs):
        "ArgParser (svg)."
        logger = getLogger()
        self.renderer = Render
        self.encode   = True # valid for png.
        self.poly     = False
        self.shadow   = None
        self.oxygen   = 0.06 # absolute radius in nm
        self.HB       = 0.4  # radius relative to the oxygen
        self.OH       = 0.5  # radius relative to the oxygen
        self.hydrogen = 0    # radius relative to the oxygen
        self.arrows   = False
        self.bgcolor  = None
        self.proj = np.array([[1., 0, 0], [0, 1, 0], [0, 0, 1]])
        self.width    = 0
        self.height   = 0
        for key, value in kwargs.items():
            logger.info("  Option with arguments: {0} := {1}".format(key,value))
            if key == "rotmat":
                value = re.search(r"\[([-0-9,.]+)\]", value).group(1)
                self.proj = np.array([float(x) for x in value.split(",")]).reshape(3,3)
            elif key == "rotatex":
                value = float(value)*pi/180
                cosx = cos(value)
                sinx = sin(value)
                R = np.array([[1, 0, 0], [0, cosx, sinx], [0,-sinx, cosx]])
                self.proj = np.dot(self.proj, R)
            elif key == "rotatey":
                value = float(value)*pi/180
                cosx = cos(value)
                sinx = sin(value)
                R = np.array([[cosx, 0, -sinx], [0, 1, 0], [sinx, 0, cosx]])
                self.proj = np.dot(self.proj, R)
            elif key == "rotatez":
                value = float(value)*pi/180
                cosx = cos(value)
                sinx = sin(value)
                R = np.array([[cosx, sinx, 0], [-sinx, cosx, 0], [0, 0, 1]])
                self.proj = np.dot(self.proj, R)
            elif key == "shadow":
                if value is True:
                    self.shadow = "#8881"
                else:
                    self.shadow = value
            elif key == "H":
                if value is True:
                    self.hydrogen = 0.6
                    self.HB = 0.2
                else:
                    self.hydrogen = float(value)
            elif key == "HB":
                self.HB = float(value)
            elif key == "O":
                self.oxygen = float(value)
            elif key == "OH":
                if value is True:
                    self.OH = 0.5
                else:
                    self.OH = float(value)
            elif key == "bg":
                self.bgcolor = value
            elif key == "width":
                self.width = int(value)
            elif key == "height":
                self.height = int(value)
            elif key == "encode":
                self.encode = bool(value)
            elif value is True:
                a = key
                logger.info("  Flags: {0}".format(a))
                if a == "polygon":
                    self.poly = True
                elif a == "arrows":
                    self.arrows = True
                else:
                    assert False, "  Wrong options."
            else:
                assert False, "  Wrong options."

    @timeit
    @banner
    def Hook2(self, lattice):
        "A. Output molecular positions in PNG/SVG format."
        logger = getLogger()
        if self.hydrogen > 0 or self.arrows:
            # draw everything in hook6
            return
        offset = np.zeros(3)

        for i in range(3):
            self.proj[i] /= np.linalg.norm(self.proj[i])
        self.proj = np.linalg.inv(self.proj)

        cellmat = lattice.repcell.mat
        projected = np.dot(cellmat, self.proj)
        pos = lattice.reppositions
        prims = []
        RO   = self.oxygen  # nm
        RHB  = self.oxygen*self.HB # nm
        xmin, xmax, ymin, ymax = draw_cell(prims, projected)
        if self.poly:
            for ring in cycles_iter(nx.Graph(lattice.graph),
                                   8,
                                   pos=lattice.reppositions):
                nedges = len(ring)
                deltas = np.zeros((nedges,3))
                d2 = np.zeros(3)
                for k,i in enumerate(ring):
                    d = lattice.reppositions[i] - lattice.reppositions[ring[0]]
                    d -= np.floor(d+0.5)
                    deltas[k] = d
                comofs = np.sum(deltas, axis=0) / len(ring)
                deltas -= comofs
                com = lattice.reppositions[ring[0]] + comofs
                com -= np.floor(com)
                # rel to abs
                com    = np.dot(com,    projected)
                deltas = np.dot(deltas, projected)
                prims.append([com, "P", deltas, {"fillhs":hue_sat[nedges]}]) # line
        else:
            for i,j in lattice.graph.edges():
                vi = pos[i]
                d  = pos[j] - pos[i]
                d -= np.floor(d+0.5)
                clipped = clip_cyl(vi@projected, RO, (vi+d)@projected, RO, RHB)
                if clipped is not None:
                    prims.append(clipped + [RHB, {"fill":"#fff"}]) # line
                if np.linalg.norm(vi+d-pos[j]) > 0.01:
                    vj = pos[j]
                    d  = pos[i] - pos[j]
                    d -= np.floor(d+0.5)
                    clipped = clip_cyl(vj@projected, RO, (vj+d)@projected, RO, RHB)
                    if clipped is not None:
                        prims.append(clipped + [RHB, {"fill":"#fff"}]) # line
            for i,v in enumerate(pos):
                prims.append([np.dot(v, projected),"C",RO, {}]) #circle
        xsize = xmax - xmin
        ysize = ymax - ymin
        zoom = 200
        if self.width > 0:
            zoom = self.width / xsize
            if self.height > 0:
                z2 = self.height / ysize
                if z2 < zoom:
                    zoom = z2
                    xsize = self.width/zoom
                    xcenter = (xmax+xmin)/2
                    xmin, xmax = xcenter-xsize/2, xcenter+xsize/2
                else:
                    ysize = self.height/zoom
                    ycenter = (ymax+ymin)/2
                    ymin, ymax = ycenter-ysize/2, ycenter+ysize/2
        elif self.height > 0:
            zoom = self.height / ysize
        logger.debug("Zoom {0} {1}x{2}".format(zoom, zoom*xsize, zoom*ysize))
        self.output = self.renderer(prims, RO,
                                    shadow=self.shadow,
                                    topleft=np.array((xmin,ymin)),
                                    size=(xsize, ysize),
                                    zoom=zoom,
                                    bgcolor=self.bgcolor,
                                    encode=self.encode)
        if self.hydrogen == 0 and not self.arrows:
            logger.info("Abort the following stages.")
            return True # abort the following stages



    @timeit
    @banner
    def Hook6(self, lattice):
        "A. Output atomic positions in PNG/SVG format."
        logger = getLogger()
        if self.hydrogen == 0 and not self.arrows:
            # draw everything in hook2
            return

        filloxygen = { "stroke_width": 1,
                         "stroke": "#444",
                         "fill": "#f00",
                         #"stroke_linejoin": "round",
                         #"stroke_linecap" : "round",
                         #"fill_opacity": 1.0,
        }
        fillhydrogen = { "stroke_width": 1,
                         "stroke": "#444",
                         "fill": "#0ff",
                         #"stroke_linejoin": "round",
                         #"stroke_linecap" : "round",
                         #"fill_opacity": 1.0,
        }
        lineOH = { "stroke_width": 1,
                   "stroke": "#444",
                   "fill": "#fff",
                   }
        lineHB = { "stroke_width": 1,
                   "stroke": "#444",
                   "fill": "#ff0",
        }
        arrow = { "stroke_width": 3,
                   "stroke": "#fff",
        }
        offset = np.zeros(3)

        # Projection to the viewport
        for i in range(3):
            self.proj[i] /= np.linalg.norm(self.proj[i])
        self.proj = np.linalg.inv(self.proj)

        cellmat = lattice.repcell.mat
        projected = np.dot(cellmat, self.proj)

        # pos = lattice.reppositions
        prims = []
        RO   = self.oxygen  # nm
        RHB  = self.oxygen*self.HB       # nm
        ROH  = self.oxygen*self.OH       # nm
        RH   = self.oxygen*self.hydrogen # nm
        waters = defaultdict(dict)
        xmin, xmax, ymin, ymax = draw_cell(prims, projected)
        if self.arrows:
            pos = lattice.reppositions
            for i,j in lattice.spacegraph.edges():
                vi = pos[i]
                d  = pos[j] - pos[i]
                d -= np.floor(d+0.5)
                clipped = clip_cyl(vi@projected, RO, (vi+d)@projected, RO, 0.0) #line
                if clipped is not None:
                    prims.append(clipped + [0.0, {"stroke":"#fff"}]) # line
                if np.linalg.norm(vi+d-pos[j]) > 0.01:
                    vj = pos[j]
                    d  = pos[i] - pos[j]
                    d -= np.floor(d+0.5)
                    clipped = clip_cyl((vj+d)@projected, RO, vj@projected, RO, 0.0)
                    if clipped is not None:
                        prims.append(clipped + [0.0, {"stroke":"#fff"}]) # line
            for i,v in enumerate(pos):
                prims.append([np.dot(v, projected),"C",RO, {}]) #circle
        else:
            atoms = []
            for mols in ice.universe:
                atoms += serialize(mols)

            for atom in atoms:
                resno, resname, atomname, position, order = atom
                if "O" in atomname:
                    waters[order]["O"] = position
                elif "H" in atomname:
                    if "H0" not in waters[order]:
                        waters[order]["H0"] = position
                    else:
                        waters[order]["H1"] = position

            # draw water molecules
            for order, water in waters.items():
                O = water["O"]
                H0 = water["H0"]
                H1 = water["H1"]
                prims.append([O  @ self.proj, "C", RO, filloxygen]) #circle
                prims.append([H0 @ self.proj, "C", RH, fillhydrogen]) #circle
                prims.append([H1 @ self.proj, "C", RH, fillhydrogen]) #circle
                # clipped cylinder
                clipped = clip_cyl(O@self.proj, RO, H0@self.proj, RH, ROH)
                if clipped is not None:
                    prims.append(clipped + [ROH, lineOH])
                clipped = clip_cyl(O@self.proj, RO, H1@self.proj, RH, ROH)
                if clipped is not None:
                    prims.append(clipped + [ROH, lineOH])
            # draw HBs
            for i,j,d in lattice.spacegraph.edges(data=True):
                if i in waters and j in waters:  # edge may connect to the dopant
                    O = waters[j]["O"]
                    H0 = waters[i]["H0"]
                    H1 = waters[i]["H1"]
                    d0 = H0 - O
                    d1 = H1 - O
                    rr0 = d0 @ d0
                    rr1 = d1 @ d1
                    if rr0 < rr1 and rr0 < 0.245**2:
                        clipped = clip_cyl(O@self.proj, RO, H0@self.proj, RH, RHB)
                        if clipped is not None:
                            prims.append(clipped + [RHB, lineHB])
                    elif rr1 < rr0 and rr1 < 0.245**2:
                        clipped = clip_cyl(O@self.proj, RO, H1@self.proj, RH, RHB)
                        if clipped is not None:
                            prims.append(clipped + [RHB, lineHB])
                    else:
                        logger.debug((np.linalg.norm(d['vector']),rr0,rr1,0.245**2))
        xsize = xmax - xmin
        ysize = ymax - ymin
        self.output = self.renderer(prims, RO,
                                    shadow=self.shadow,
                                    topleft=np.array((xmin,ymin)),
                                    size=(xsize, ysize),
                                    bgcolor=self.bgcolor,
                                    encode=self.encode)
