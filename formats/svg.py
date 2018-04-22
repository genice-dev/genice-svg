# coding: utf-8
"""
Yaplot format.
defined in https://github.com/vitroid/Yaplot
"""

import colorsys
import numpy as np
import yaplotlib as yp
from math import sin,cos
import svgwrite as sw


def hook2(lattice):
    lattice.logger.info("Hook2: A. Output molecular positions in SVG format.")
    offset = np.zeros(3)

    sun = np.array([1., -10., 5.])  # right, down, front
    sun /= np.linalg.norm(sun)

    proj = np.array([[-3**0.5/2, 1./2.],
                     [+3**0.5/2, 1./2.],
                     [0.,       -1.]])


    proj = np.array([[1., -1., 0.], [1., 1., -2.], [1., 1., 1.]])
    proj = np.identity(3)
    theta = 0.0
    smallrot = np.array([[cos(theta),-sin(theta),0.],
                         [+sin(theta),cos(theta),0.],
                         [0.,0.,1.0]])

    for i in range(3):
        proj[i] /= np.linalg.norm(proj[i])
    proj = np.dot(proj,smallrot)
    proj = np.linalg.inv(proj)

    cellmat = lattice.cell.mat
    projected = np.dot(cellmat, proj)
    pos = lattice.reppositions
    prims = []
    R = 0.025
    for i,j in lattice.graph.edges():
        vi = pos[i]
        d  = pos[j] - pos[i]
        d -= np.floor(d+0.5)
        center = vi+d/2
        dp = np.dot(d, projected)
        o = dp / np.linalg.norm(dp)
        o *= R
        prims.append((np.dot(center,projected), np.dot(vi,projected)+o, np.dot(vi+d,projected)-o)) # line
    for i,v in enumerate(pos):
        prims.append((np.dot(v, projected),i)) #circle
    svg = sw.Drawing()
    for prim in sorted(prims, key=lambda x: x[0][2]):
        if len(prim) == 3: #line
            svg.add(sw.shapes.Line(start=prim[1][:2]*200+200, end=prim[2][:2]*200+200, stroke_width=2, stroke="#444", stroke_linejoin="round", stroke_linecap="round"))
        else:
            order = prim[1]%152
            if 0 <= order < 32:
                pal=0
                col="#777"
            elif 32 <= order < 48:
                pal=1
                col="#00C"
            elif 48<= order < 80:
                pal=2
                col="#7DD"
            elif 80<=order<112:
                pal=3
                col="#7D4"
            elif 112<=order<144:
                pal=4
                col="#CA2"
            else:
                pal=5
                col="#B00"
            hue = pal/6. # ((5**0.5-1)/2*pal)%1
            sat = 1
            bri = 1
            r,g,b = colorsys.hsv_to_rgb(hue, sat, bri)
            rgb = "#{0:x}{1:x}{2:x}".format(int(r*15.9), int(g*15.9), int(b*15.9))
            svg.add(sw.shapes.Circle(center=prim[0][:2]*200+200, r=R*200, stroke_width=1, stroke="#000", fill=col))
    print(svg.tostring())
    lattice.logger.info("Hook2: end.")


hooks = {2:hook2}
