from collections import defaultdict

import numpy as np
import networkx as nx
import sys
from attrdict import AttrDict
from logging import getLogger

from countrings import countrings_nx as cr

hue_sat = {3:(60., 0.8),
           4:(120, 0.8), # yellow-green
           5:(180, 0.5), # skyblue
           6:(240, 0.5), # blue
           7:(300, 0.8), #
           8:(350, 0.5)} # red-purple

options = AttrDict()


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



def hook2(lattice):
    logger = getLogger()
    if options.hydrogen > 0 or options.arrows:
        # draw everything in hook6
        return 
    logger.info("Hook2: A. Output molecular positions in PNG/SVG format.")
    offset = np.zeros(3)

    for i in range(3):
        options.proj[i] /= np.linalg.norm(options.proj[i])
    options.proj = np.linalg.inv(options.proj)

    cellmat = lattice.repcell.mat
    projected = np.dot(cellmat, options.proj)
    pos = lattice.reppositions
    prims = []
    RO   = options.oxygen  # nm
    RHB  = options.oxygen*options.HB # nm
    xmin, xmax, ymin, ymax = draw_cell(prims, projected)
    if options.poly:
        for ring in cr.CountRings(nx.Graph(lattice.graph), pos=lattice.reppositions).rings_iter(8):
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
    if options.width > 0:
        zoom = options.width / xsize
        if options.height > 0:
            z2 = options.height / ysize
            if z2 < zoom:
                zoom = z2
                xsize = options.width/zoom
                xcenter = (xmax+xmin)/2
                xmin, xmax = xcenter-xsize/2, xcenter+xsize/2
            else:
                ysize = options.height/zoom
                ycenter = (ymax+ymin)/2
                ymin, ymax = ycenter-ysize/2, ycenter+ysize/2
    elif options.height > 0:
        zoom = options.height / ysize
    logger.debug("Zoom {0} {1}x{2}".format(zoom, zoom*xsize, zoom*ysize))
    options.renderer(prims, RO, shadow=options.shadow,
                     topleft=np.array((xmin,ymin)),
                     size=(xsize, ysize), zoom=zoom, bgcolor=options.bgcolor)
    logger.info("Hook2: end.")
    if options.hydrogen == 0 and not options.arrows:
        logger.info("Abort the following stages.")
        return True # abort the following stages



def hook6(lattice):
    logger = getLogger()
    if options.hydrogen == 0 and not options.arrows:
        # draw everything in hook2
        return 
    logger.info("Hook6: A. Output atomic positions in PNG/SVG format.")

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
        options.proj[i] /= np.linalg.norm(options.proj[i])
    options.proj = np.linalg.inv(options.proj)

    cellmat = lattice.repcell.mat
    projected = np.dot(cellmat, options.proj)
    
    # pos = lattice.reppositions
    prims = []
    RO   = options.oxygen  # nm
    RHB  = options.oxygen*options.HB       # nm
    ROH  = options.oxygen*options.OH       # nm
    RH   = options.oxygen*options.hydrogen # nm
    waters = defaultdict(dict)
    xmin, xmax, ymin, ymax = draw_cell(prims, projected)
    if options.arrows:
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
        for atom in options.atoms:
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
            prims.append([O  @ options.proj, "C", RO, filloxygen]) #circle
            prims.append([H0 @ options.proj, "C", RH, fillhydrogen]) #circle
            prims.append([H1 @ options.proj, "C", RH, fillhydrogen]) #circle
            # clipped cylinder
            clipped = clip_cyl(O@options.proj, RO, H0@options.proj, RH, ROH)
            if clipped is not None:
                prims.append(clipped + [ROH, lineOH])
            clipped = clip_cyl(O@options.proj, RO, H1@options.proj, RH, ROH)
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
                    clipped = clip_cyl(O@options.proj, RO, H0@options.proj, RH, RHB)
                    if clipped is not None:
                        prims.append(clipped + [RHB, lineHB])
                elif rr1 < rr0 and rr1 < 0.245**2:
                    clipped = clip_cyl(O@options.proj, RO, H1@options.proj, RH, RHB)
                    if clipped is not None:
                        prims.append(clipped + [RHB, lineHB])
                else:
                    logger.debug((np.linalg.norm(d['vector']),rr0,rr1,0.245**2))
    xsize = xmax - xmin
    ysize = ymax - ymin
    options.renderer(prims, RO, shadow=options.shadow,
                 topleft=np.array((xmin,ymin)),
                     size=(xsize, ysize), bgcolor=options.bgcolor)
    logger.info("Hook6: end.")


# argparser

#New standard style of options for the plugins:
#svg2[rotmat=[]:other=True:...]

