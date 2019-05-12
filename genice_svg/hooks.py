from collections import defaultdict

import numpy as np

def clip_cyl(v1, r1, v2, r2):
    dv = v2 - v1
    Lv = np.linalg.norm(dv)
    if Lv < r1+r2:
        return None
    newv1 = v1 + dv*r1/Lv
    newv2 = v2 - dv*r2/Lv
    c = (newv1+newv2)/2
    d = newv2-c
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
    if lattice.hydrogen > 0:
        # draw everything in hook6
        return 
    lattice.logger.info("Hook2: A. Output molecular positions in PNG/SVG format.")
    offset = np.zeros(3)

    for i in range(3):
        lattice.proj[i] /= np.linalg.norm(lattice.proj[i])
    lattice.proj = np.linalg.inv(lattice.proj)

    cellmat = lattice.repcell.mat
    projected = np.dot(cellmat, lattice.proj)
    pos = lattice.reppositions
    prims = []
    Rsphere = lattice.oxygen  # nm
    Rcyl    = lattice.oxygen*lattice.HB # nm
    xmin, xmax, ymin, ymax = draw_cell(prims, projected)
    for i,j in lattice.graph.edges():
        vi = pos[i]
        d  = pos[j] - pos[i]
        d -= np.floor(d+0.5)
        clipped = clip_cyl(vi@projected, Rsphere, (vi+d)@projected, Rsphere)
        if clipped is not None:
            prims.append(clipped + [Rcyl, {"fill":"#fff"}]) # line
        if np.linalg.norm(vi+d-pos[j]) > 0.01:
            vj = pos[j]
            d  = pos[i] - pos[j]
            d -= np.floor(d+0.5)
            clipped = clip_cyl(vj@projected, Rsphere, (vj+d)@projected, Rsphere)
            if clipped is not None:
                prims.append(clipped + [Rcyl, {"fill":"#fff"}]) # line

    for i,v in enumerate(pos):
        prims.append([np.dot(v, projected),"C",Rsphere, {}]) #circle
    xsize = xmax - xmin
    ysize = ymax - ymin
    image = lattice.renderer(prims, Rsphere, shadow=lattice.shadow,
                 topleft=np.array((xmin,ymin)),
                 size=(xsize, ysize))
    imgByteArr = io.BytesIO()
    image.save(imgByteArr, format='PNG')
    imgByteArr = imgByteArr.getvalue()
    sys.stdout.buffer.write(imgByteArr)
    lattice.logger.info("Hook2: end.")



def hook6(lattice):
    if lattice.hydrogen == 0:
        # draw everything in hook2
        return 
    lattice.logger.info("Hook6: A. Output atomic positions in PNG format.")

    filloxygen = { "stroke_width": 1,
                     "stroke": "#888",
                     "fill": "#f88",
                     #"stroke_linejoin": "round",
                     #"stroke_linecap" : "round",
                     #"fill_opacity": 1.0,
    }
    fillhydrogen = { "stroke_width": 1,
                     "stroke": "#888",
                     "fill": "#8ff",
                     #"stroke_linejoin": "round",
                     #"stroke_linecap" : "round",
                     #"fill_opacity": 1.0,
    }
    lineOH = { "stroke_width": 1,
               "stroke": "#888",
               "fill": "#fff",
    }
    offset = np.zeros(3)

    # Projection to the viewport
    for i in range(3):
        lattice.proj[i] /= np.linalg.norm(lattice.proj[i])
    lattice.proj = np.linalg.inv(lattice.proj)

    cellmat = lattice.repcell.mat
    projected = np.dot(cellmat, lattice.proj)
    
    # pos = lattice.reppositions
    prims = []
    Rsphere = lattice.oxygen  # nm
    Rcyl    = lattice.oxygen*lattice.HB       # nm
    ROH     = lattice.oxygen*lattice.OH       # nm
    RH      = lattice.oxygen*lattice.hydrogen # nm
    waters = defaultdict(dict)
    xmin, xmax, ymin, ymax = draw_cell(prims, projected)

    for atom in lattice.atoms:
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
        prims.append([O  @ lattice.proj, "C", Rsphere, filloxygen]) #circle
        prims.append([H0 @ lattice.proj, "C", RH, fillhydrogen]) #circle
        prims.append([H1 @ lattice.proj, "C", RH, fillhydrogen]) #circle
        # clipped cylinder
        clipped = clip_cyl(O@lattice.proj, Rsphere, H0@lattice.proj, RH)
        if clipped is not None:
            prims.append(clipped + [ROH, lineOH])
        clipped = clip_cyl(O@lattice.proj, Rsphere, H1@lattice.proj, RH)
        if clipped is not None:
            prims.append(clipped + [ROH, lineOH])
    # for i,j in lattice.graph.edges():
    #     vi = pos[i]
    #     d  = pos[j] - pos[i]
    #     d -= np.floor(d+0.5)
    #     center = vi+d/2
    #     dp = np.dot(d, projected)
    #     o = dp / np.linalg.norm(dp)
    #     o *= RR
    #     prims.append([np.dot(center,projected), "L", np.dot(vi,projected)+o, np.dot(vi+d,projected)-o,Rcyl, {"fill":"#fff"}]) # line
    #     if np.linalg.norm(vi+d-pos[j]) > 0.01:
    #         vj = pos[j]
    #         d  = pos[i] - pos[j]
    #         d -= np.floor(d+0.5)
    #         center = vj+d/2
    #         dp = np.dot(d, projected)
    #         o = dp / np.linalg.norm(dp)
    #         o *= RR
    #         prims.append([np.dot(center,projected), "L", np.dot(vj,projected)+o, np.dot(vj+d,projected)-o,Rcyl, {"fill":"#fff"}]) # line

    #for i,v in enumerate(pos):
    xsize = xmax - xmin
    ysize = ymax - ymin
    lattice.renderer(prims, Rsphere, shadow=lattice.shadow,
                 topleft=np.array((xmin,ymin)),
                 size=(xsize, ysize))
    lattice.logger.info("Hook6: end.")


# argparser

#New standard style of options for the plugins:
#svg2[rotmat=[]:other=True:...]

