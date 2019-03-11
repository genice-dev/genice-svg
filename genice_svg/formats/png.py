# coding: utf-8
"""
PNG, derived from SVG format rev. 2
"""

import colorsys
import numpy as np
import yaplotlib as yp
from math import sin,cos, atan2,pi, exp
import re
import logging
from countrings import countrings_nx as cr
import networkx as nx
import PIL.ImageDraw as ImageDraw
import PIL.Image as Image
import io
import sys

def cylinder(draw, v1_, v2_, r, **options):
    """
    draw a 3D cylinder
    """
    options = {"fill": "#fff", **options}
    draw.line([int(x) for x in [v1_[0], v1_[1], v2_[0], v2_[1]]],
              width=int(r*2), fill=options["fill"])
    


# def polygon_path(vs, **kwargs):
#     p = []
#     p.append(["M", vs[-1][0], vs[-1][1]])
#     for v in vs:
#         p.append(["L", v[0], v[1]])
#     p.append(["Z"])
#     return sw.path.Path(d=p, **kwargs)



# def polygon(svg, com, d, **options):
#     """
#     draw a polygon
#     """
#     group = svg.add( svg.g( id='Polygon') )
#     path = polygon_path(com+d, **options)
#     group.add(path)
    

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



def Render(prims, Rsphere, shadow=None, topleft=np.array([-1.,-1.]), size=(50,50), zoom=200):
    logger = logging.getLogger()
    size = tuple((int(x*zoom) for x in size))
    image = Image.new("RGB", size, (0,0,0))
    draw  = ImageDraw.Draw(image, "RGBA")
    # special treatment for post-K project
    # draw.rectangle([0,0,size[0]/2,size[1]], fill="#EF5FA7")
    # draw.rectangle([size[0]/2,0,size[0],size[1]], fill="#00A2FF")
    
    TL0 = np.zeros(3)
    TL0[:2] = topleft
    shadows = []
    linedefaults = { "stroke_width": 2,
                     "stroke": "#000",
                     #"stroke_linejoin": "round",
                     #"stroke_linecap" : "round",
    }
    filldefaults = { "stroke_width": 1,
                     "stroke": "#000",
                     "fill": "#0ff",
                     #"stroke_linejoin": "round",
                     #"stroke_linecap" : "round",
                     #"fill_opacity": 1.0,
    }
    shadowdefaults = { "stroke_width": 0,
                       #"fill": "#8881",
                       "fill": shadow,
                       #"fill_opacity": 0.08,
    }
    if shadow is not None:
        for prim in prims:
            r = prim[2]
            ofs = np.array([0,0,r])
            if prim[1] == "C":
                shadows.append([prim[0] - ofs, prim[1]+"S", r*1.4]+prim[3:])
                shadows.append([prim[0] - ofs*1.4**2, prim[1]+"S", r*1.4**2]+prim[3:])
                shadows.append([prim[0] - ofs*1.4**3, prim[1]+"S", r*1.4**3]+prim[3:])
                shadows.append([prim[0] - ofs*1.4**4, prim[1]+"S", r*1.4**4]+prim[3:])
    prims += shadows
    for prim in sorted(prims, key=lambda x: x[0][2]):
        if not ( (-0.5 < prim[0][0]-topleft[0] < size[0]+0.5) and
                 (-0.5 < prim[0][1]-topleft[1] < size[1]+0.5) ):
            continue
        if prim[1] == "L":
            if prim[4] == 0:
                options = {**linedefaults, **prim[5]}
                s = (prim[2][:2]-topleft)*zoom
                e = (prim[3][:2]-topleft)*zoom
                draw.line([int(s[0]), int(s[1]), int(e[0]), int(e[1])], fill=options["stroke"], width=options["stroke_width"])
            else:
                options = {**filldefaults, **prim[5]}
                cylinder(draw, (prim[2]-TL0)*zoom, (prim[3]-TL0)*zoom, prim[4]*zoom, **options)
        elif prim[1] == "L2":
            #new, simpler expression.
            #half relative vector is given
            if prim[3] == 0:
                options = {**linedefaults, **prim[4]}
                s = ((prim[0]+prim[2])[:2]-topleft)*zoom
                e = ((prim[0]-prim[2])[:2]-topleft)*zoom
                draw.line([int(s[0]), int(s[1]), int(e[0]), int(e[1])], fill=options["stroke"], width=options["stroke_width"])
            else:
                options = {**filldefaults, **prim[4]}
                cylinder(draw, (prim[0]+prim[2]-TL0)*zoom, (prim[0]-prim[2]-TL0)*zoom, prim[3]*zoom, **options)
        # elif prim[1] == "P":
        #     options = prim[3]
        #     if "fillhs" in options:
        #         normal = Normal(prim[2])
        #         normal /= np.linalg.norm(normal)
        #         cosine = abs(np.dot(sun, normal))
        #         hue, sat = options["fillhs"]
        #         del options["fillhs"]
        #         bri = cosine*0.5+0.5
        #         if sat < 0.2:
        #             bri *= 0.9
        #         if cosine > 0.8:
        #             sat *= (1 - (cosine-0.8)*3)
        #         r,g,b = colorsys.hsv_to_rgb(hue/360., sat, bri)
        #         rgb = "#{0:x}{1:x}{2:x}".format(int(r*15.9), int(g*15.9), int(b*15.9))
        #         options["fill"] = rgb
        #     options = {**filldefaults, **options}
        #     polygon(svg, (prim[0]-TL0)*zoom, prim[2]*zoom, **options)
        elif prim[1] == "C":
            options = { **filldefaults, **prim[3] }
            Rsphere = prim[2]
            center=(prim[0][:2]-topleft)*zoom
            r=Rsphere*zoom
            tl = center-r
            br = center+r
            draw.ellipse([int(x) for x in [tl[0], tl[1], br[0], br[1]]], fill=options["fill"])
        elif prim[1] == "CS":
            Rsphere = prim[2]
            options = { **shadowdefaults,} #  **prim[3] }
            # logger.info("{0}".format(options))
            center=(prim[0][:2]-topleft)*zoom
            r=Rsphere*zoom
            tl = center-r
            br = center+r
            
            draw.ellipse([int(x) for x in [tl[0], tl[1], br[0], br[1]]], fill=options["fill"])
    return image
        
# set of hue and saturation
hue_sat = {3:(60., 0.8),
           4:(120, 0.8), # yellow-green
           5:(180, 0.5), # skyblue
           6:(240, 0.5), # blue
           7:(300, 0.8), #
           8:(350, 0.5)} # red-purple

def hook2(lattice):
    lattice.logger.info("Hook2: A. Output molecular positions in PNG format. (Improved)")
    offset = np.zeros(3)

    for i in range(3):
        lattice.proj[i] /= np.linalg.norm(lattice.proj[i])
    lattice.proj = np.linalg.inv(lattice.proj)

    cellmat = lattice.repcell.mat
    projected = np.dot(cellmat, lattice.proj)
    pos = lattice.reppositions
    prims = []
    Rsphere = 0.06  # nm
    Rcyl    = 0.03  # nm
    RR      = (Rsphere**2 - Rcyl**2)**0.5
    xmin, xmax, ymin, ymax = draw_cell(prims, projected)
    if lattice.poly:
        for ring in cr.CountRings(nx.Graph(lattice.graph)).rings_iter(8):
            nedges = len(ring)
            deltas = np.zeros((nedges,3))
            d2 = np.zeros(3)
            for k,i in enumerate(ring):
                d = lattice.reppositions[i] - lattice.reppositions[ring[0]]
                d -= np.floor(d+0.5)
                deltas[k] = d
                dd = lattice.reppositions[ring[k]] - lattice.reppositions[ring[k-1]]
                dd -= np.floor(dd+0.5)
                d2 += dd
            # d2 must be zeros
            if np.all(np.absolute(d2) < 1e-5):
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
            center = vi+d/2
            dp = np.dot(d, projected)
            o = dp / np.linalg.norm(dp)
            o *= RR
            prims.append([np.dot(center,projected), "L", np.dot(vi,projected)+o, np.dot(vi+d,projected)-o,Rcyl, {"fill":"#fff"}]) # line
            if np.linalg.norm(vi+d-pos[j]) > 0.01:
                vj = pos[j]
                d  = pos[i] - pos[j]
                d -= np.floor(d+0.5)
                center = vj+d/2
                dp = np.dot(d, projected)
                o = dp / np.linalg.norm(dp)
                o *= RR
                prims.append([np.dot(center,projected), "L", np.dot(vj,projected)+o, np.dot(vj+d,projected)-o,Rcyl, {"fill":"#fff"}]) # line

        for i,v in enumerate(pos):
            prims.append([np.dot(v, projected),"C",Rsphere, {}]) #circle
    xsize = xmax - xmin
    ysize = ymax - ymin
    image = Render(prims, Rsphere, shadow=lattice.shadow,
                 topleft=np.array((xmin,ymin)),
                 size=(xsize, ysize))
    imgByteArr = io.BytesIO()
    image.save(imgByteArr, format='PNG')
    imgByteArr = imgByteArr.getvalue()
    sys.stdout.buffer.write(imgByteArr)
    lattice.logger.info("Hook2: end.")




# argparser

#New standard style of options for the plugins:
#svg2[rotmat=[]:other=True:...]

def hook0(lattice, arg):
    lattice.logger.info("Hook0: ArgParser.")
    lattice.shadow = None
    lattice.poly = False
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
            else:
                lattice.logger.info("Flags: {0}".format(a))
                if a == "shadow":
                    lattice.shadow = "#8881"
                #elif a == "polygon":
                #    lattice.poly = True
                else:
                    assert False, "Wrong options."
    lattice.logger.info("Hook0: end.")


def main():
    #print(atan2(sin(3),cos(3)))
    image = Image.new("RGB", (1000,1000))
    draw = ImageDraw.Draw(image, "RGBA")
    cylinder(draw, np.array((20.,20.,20.)),np.array((100.,20.,100.)),15.)
    image.save("test.png")
    
if __name__ == "__main__":
    main()

hooks = {0:hook0, 2:hook2}

