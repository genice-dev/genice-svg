# coding: utf-8
"""
SVG format rev. 2 developed for Prof. Tanaka
"""

import colorsys
import numpy as np
import yaplotlib as yp
from math import sin,cos, atan2,pi, exp
import svgwrite as sw


def cylinder(svg, v1_, v2_, r, fill="#fff"):
    """
    draw a 3D cylinder
    """
    group = svg.add( svg.g( id='Cylinder') )
    if v1_[2] > v2_[2]:
        v1, v2 = v2_, v1_
    else:
        v1, v2 = v1_, v2_
    dir = v2[:2] - v1[:2]
    angle = atan2(dir[1],dir[0])
    # e   = dir / np.linalg.norm(dir)
    # ee  = np.array([e[1], -e[0]])
    d   = v2 - v1
    ratio = d[2] / np.linalg.norm(d)
    u = sw.shapes.Ellipse(center=v1[:2], r=(ratio*r, r), stroke_width=1, stroke="#000", fill=fill)
    u.rotate(angle*180/pi, center=v1[:2])
    group.add(u)
    u = sw.shapes.Rect((v1[0],v1[1]-r), (np.linalg.norm(dir), 2*r), stroke_width=0, stroke="#000", fill=fill)
    u.rotate(angle*180/pi, center=v1[:2])
    group.add(u)
    u = sw.shapes.Ellipse(center=v2[:2], r=(ratio*r, r), stroke_width=1, stroke="#000", fill="#ddd")
    u.rotate(angle*180/pi, center=v2[:2])
    group.add(u)
    u = sw.shapes.Line((v1[0],v1[1]-r), (v1[0]+np.linalg.norm(dir), v1[1]-r), stroke_width=1, stroke="#000")
    u.rotate(angle*180/pi, center=v1[:2])
    group.add(u)
    u = sw.shapes.Line((v1[0],v1[1]+r), (v1[0]+np.linalg.norm(dir), v1[1]+r), stroke_width=1, stroke="#000")
    u.rotate(angle*180/pi, center=v1[:2])
    group.add(u)
    
    


def draw_cell(prims, cellmat):
    for a in (0., 1.):
        for b in (0., 1.):
            v0 = np.array([0., a, b])
            v1 = np.array([1., a, b])
            mid = (v0+v1)/2
            prims.append([np.dot(mid, cellmat),
                          "L",
                          np.dot(v0,  cellmat),
                          np.dot(v1,  cellmat), 0])
            v0 = np.array([b, 0., a])
            v1 = np.array([b, 1., a])
            mid = (v0+v1)/2
            prims.append([np.dot(mid, cellmat),
                          "L",
                          np.dot(v0,  cellmat),
                          np.dot(v1,  cellmat), 0])
            v0 = np.array([a, b, 0.])
            v1 = np.array([a, b, 1.])
            mid = (v0+v1)/2
            prims.append([np.dot(mid, cellmat),
                          "L",
                          np.dot(v0,  cellmat),
                          np.dot(v1,  cellmat), 0])
            

def Render(svg, prims, Rsphere, shadow=True):
    shadows = []
    if shadow:
        for prim in prims:
            ofs = np.array([0,0,0.2])
            p2 = [prim[0] - ofs, prim[1]+"S", prim[2:]]
            shadows.append(p2)
    prims += shadows
    for prim in sorted(prims, key=lambda x: x[0][2]):
        if prim[1] == "L":
            # svg.add(sw.shapes.Line(start=prim[1][:2]*200+200, end=prim[2][:2]*200+200, stroke_width=2, stroke="#444", stroke_linejoin="round", stroke_linecap="round"))
            if prim[4] == 0:
                svg.add(sw.shapes.Line(start=prim[2][:2]*200+200, end=prim[3][:2]*200+200, stroke_width=2, stroke="#444", stroke_linejoin="round", stroke_linecap="round"))
            else:
                cylinder(svg, prim[2]*200+200, prim[3]*200+200, prim[4]*200)
        elif prim[1] == "C":
            z = prim[0][1]
            zr = z - 3.2
            zs = 1-1/(1+exp(zr*15))
            red = 0
            gre = 128+int((1-zs)*127)
            blu = 255
            col = "#{0:02x}{1:02x}{2:02x}".format(red,gre,blu)
            svg.add(sw.shapes.Circle(center=prim[0][:2]*200+200, r=Rsphere*200, stroke_width=1, stroke="#000", fill=col))
        elif prim[1] == "CS":
            col = "#444"
            svg.add(sw.shapes.Circle(center=prim[0][:2]*200+200, r=Rsphere*200*1.4**3, stroke_width=0, fill=col, fill_opacity=0.15))
            svg.add(sw.shapes.Circle(center=prim[0][:2]*200+200, r=Rsphere*200*1.4**2, stroke_width=0, fill=col, fill_opacity=0.15))
            svg.add(sw.shapes.Circle(center=prim[0][:2]*200+200, r=Rsphere*200*1.4**1, stroke_width=0, fill=col, fill_opacity=0.15))
        

def hook2(lattice):
    lattice.logger.info("Hook2: A. Output molecular positions in SVG format. (Improved)")
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

    cellmat = lattice.repcell.mat
    projected = np.dot(cellmat, proj)
    pos = lattice.reppositions
    prims = []
    Rsphere = 0.06  # nm
    Rcyl    = 0.03  # nm
    RR      = (Rsphere**2 - Rcyl**2)**0.5
    draw_cell(prims, cellmat)
    for i,j in lattice.graph.edges():
        vi = pos[i]
        d  = pos[j] - pos[i]
        d -= np.floor(d+0.5)
        center = vi+d/2
        dp = np.dot(d, projected)
        o = dp / np.linalg.norm(dp)
        o *= RR
        prims.append([np.dot(center,projected), "L", np.dot(vi,projected)+o, np.dot(vi+d,projected)-o,Rcyl]) # line
        if np.linalg.norm(vi+d-pos[j]) > 0.01:
            vj = pos[j]
            d  = pos[i] - pos[j]
            d -= np.floor(d+0.5)
            center = vj+d/2
            dp = np.dot(d, projected)
            o = dp / np.linalg.norm(dp)
            o *= RR
            prims.append([np.dot(center,projected), "L", np.dot(vj,projected)+o, np.dot(vj+d,projected)-o,Rcyl]) # line
            
    for i,v in enumerate(pos):
        prims.append([np.dot(v, projected),"C",i]) #circle
    svg = sw.Drawing()
    Render(svg, prims, Rsphere)
    print(svg.tostring())
    lattice.logger.info("Hook2: end.")


def main():
    #print(atan2(sin(3),cos(3)))
    svg = sw.Drawing()
    cylinder(svg, np.array((20.,20.,20.)),np.array((100.,20.,100.)),15.)
    print(svg.tostring())
    
if __name__ == "__main__":
    main()

hooks = {2:hook2}

