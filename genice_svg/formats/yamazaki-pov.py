#!/usr/bin/env python

# 山崎君の構造を表示するための特製プログラム

# standard library
import logging
from collections import defaultdict
import sys
import os


# extra library
import numpy as np
import pairlist as pl
import networkx as nx
from countrings import countrings_nx as cr


# private library
import svg

# from povray.py
def Block(name, content):
    return " " + name + " { " + content + " } "

def Vector(v):
    return "<{0:.3f}, {1:.3f}, {2:.3f}> ".format(*v)

def Juxtapose(v):
    return ",".join(v)

def Atom(atomtype, pos):
    return Block( "sphere", Juxtapose( [Vector(pos), "R{0}".format(atomtype) ] ) + Block( "material", "MAT{0}".format(atomtype) ) ) + "\n"
    
def Bond(bondtype, pos1, pos2):
    return Block( "cylinder", Juxtapose( [Vector(pos1), Vector(pos2), "R{0}".format(bondtype)] ) + Block( "material", "MAT{0}".format(bondtype) ) ) + "\n"

def Box(bondtype, pos1, pos2):
    return Block( "box", Juxtapose( [Vector(pos1), Vector(pos2)] ) + Block( "material", "MAT{0}".format(bondtype) ) ) + "\n"

def SmoothTriangle(facetype, v, n):
    return Block( "smooth_triangle", Juxtapose( [
        Vector(v[0]),
        Vector(n[0]),
        Vector(v[1]),
        Vector(n[1]),
        Vector(v[2]),
        Vector(n[2]) ] ) + Block( "material", "MAT{0}".format(facetype) ) ) + "\n"

def Laser(v1, v2, r, color):
    return Block("light_group",
                 Block("light_source",Vector(v1)+" color {0} cylinder point_at ".format(color) + Vector(v2) + "radius {0} falloff {0} tightness 5 ".format(r) + Block("photons", "reflection on"))
                 + Block("merge",
                         Block("cylinder", Juxtapose([Vector(v1), Vector(v2), "{0}".format(r*2)])) + " hollow "
                         + Block("material", "transparent_with_media")
                         + Block("photons", "pass_through")
                         + " no_shadow")
                  + "global_lights off ")


def Polygon(facetype, center, vertices, rim=None):
    n = np.zeros_like(vertices)
    nc = np.zeros(3)
    s = ""
    for i in range(vertices.shape[0]):
        normal = np.cross(vertices[i] - vertices[i-1],
                        vertices[i-1] - vertices[i-2])
        normal /= np.linalg.norm(normal)
        n[i-1] = normal
        #s += "{0} {1} {2}\n".format(i-1, vertices[i-1], normal)
        nc += normal
    nc /= np.linalg.norm(nc)
    for i in range(vertices.shape[0]):
        vs = np.zeros((6,3))
        ns = np.zeros((6,3))
        vs[0] = center
        vs[1] = center + vertices[i-1]
        vs[2] = center + vertices[i]
        ns[0] = nc
        ns[1] = n[i-1]
        ns[2] = n[i]
        s += SmoothTriangle(facetype, vs, ns)
    if rim is not None:
        for i in range(vertices.shape[0]):
            s += Bond(rim,
                    center + vertices[i-1],
                    center + vertices[i])
    return s

# modified from genice/lattice.py
class mdview(): # for analice
    def __init__(self, file):
        self.file = file
    def load_iter(self):
        logger = logging.getLogger()
        au = 0.052917721067 # nm
        while True:
            line = self.file.readline() #1st line:comment
            if len(line) == 0:
                return
            cols = line.split()
            assert cols[0] == '#' #yaga style
            c = [float(x) for x in cols[1:4]]
            self.cell = np.array([[c[0],0.,0.],
                                  [0.,c[1],0.],
                                  [0.,0.,c[2]]])
            self.cell *= au
            celli = np.linalg.inv(self.cell)
            line = self.file.readline()
            natom = int(line)
            atoms = defaultdict(list)
            for i in range(natom):
                line = self.file.readline()
                cols = line.split()
                atomname = cols[0]
                pos = np.array([float(x) for x in cols[1:4]]) * au
                # pos[1] -= 0.3 # small slide 3 AA
                pos = np.dot(pos,celli) #to relative
                pos -= np.floor(pos) # wrap
                atoms[atomname].append(pos)
            yield atoms
            del atoms

logging.basicConfig(level=logging.INFO,
                    format="%(levelname)s %(message)s")
logger = logging.getLogger()

proj = np.array(([0.0, 1.0, 0.0], [0.25, 0.0, (1.0 - 0.25**2)**0.5], [1.0, 0.0, 0.0]))
drawLase = False
laserColor = "White"
laserWidth = 0.18
if len(sys.argv) > 1 and sys.argv[1][0] == "L":
    drawLaser=True
    cols = sys.argv[1].split("=")
    if len(cols) > 1:
        arg = cols[1]
        cols = arg.split(":")
        laserColor = cols[0]
        laserWidth = float(cols[1])
#mdv = mdview(sys.stdin)
#for frame, atoms in enumerate(mdv.load_iter()):
#    outfilename = "{1}{0:05d}.svg".format(frame, name)
#    if os.path.exists(outfilename):
#        logger.info("Skip frame {0}".format(frame))
#        continue

#for single file
if True:
    mdv = mdview(sys.stdin)
    atomss = [atoms for atoms in mdv.load_iter()]
    atoms = atomss[0]
    for a in atoms:
        atoms[a] = np.array(atoms[a])
    s = ""
    # Carbon
    grid200 = pl.determine_grid(mdv.cell, 0.200)
    CNT = nx.Graph([(i,j) for i,j in pl.pairs_fine(atoms['C'], 0.2, mdv.cell, grid200, distance=False)])
    for i,j in CNT.edges():
        vi = atoms['C'][i]
        vj = atoms['C'][j]
        dv = vj-vi
        dv -= np.floor(dv + 0.5)
        s += Bond('C', np.dot(vi, mdv.cell), np.dot(vi+dv, mdv.cell))
    # Water
    grid300 = pl.determine_grid(mdv.cell, 0.300)
    HBN = nx.Graph([(i,j) for i,j in pl.pairs_fine(atoms['Os'], 0.3, mdv.cell, grid300, distance=False)])
    for i,j in HBN.edges():
        vi = atoms['Os'][i]
        vj = atoms['Os'][j]
        dv = vj-vi
        dv -= np.floor(dv + 0.5)
        # s += Bond('O', np.dot(vi, mdv.cell), np.dot(vi+dv, mdv.cell))
    for ring in cr.CountRings(HBN).rings_iter(8):
        N = len(ring)
        v = np.zeros((N,3))
        for i,j in enumerate(ring):
            v[i] = atoms['Os'][j]
        ori = v[0].copy()
        v -= ori
        v -= np.floor( v + 0.5 )
        v += ori
        com = np.sum(v, axis=0) / N
        v -= com
        s += Polygon("G", np.dot(com, mdv.cell), np.dot(v, mdv.cell), rim="O")
    print("#include \"default.inc\"")
    print(Block("#declare UnitCell=union",s)+";")
    for x in range(-2,2): #large == right
        for y in range(-2,2): # large == lower
    #for x in range(0,1): #large == right
    #    for y in range(0,1): # large == lower
            print(Block("object", Juxtapose(["UnitCell translate "+Vector(mdv.cell[0]*x+mdv.cell[1]*y)])))
            if drawLaser:
                print(Laser(np.dot(np.array([0.375+x,0.25+y,-100000]), mdv.cell),
                            np.dot(np.array([0.375+x,0.25+y,+100000]), mdv.cell), laserWidth, laserColor))
                print(Laser(np.dot(np.array([0.875+x,0.25+y,-100000]), mdv.cell),
                            np.dot(np.array([0.875+x,0.25+y,+100000]), mdv.cell), laserWidth, laserColor))
                print(Laser(np.dot(np.array([0.125+x,0.75+y,-100000]), mdv.cell),
                            np.dot(np.array([0.125+x,0.75+y,+100000]), mdv.cell), laserWidth, laserColor))
                print(Laser(np.dot(np.array([0.625+x,0.75+y,-100000]), mdv.cell),
                            np.dot(np.array([0.625+x,0.75+y,+100000]), mdv.cell), laserWidth, laserColor))
                
"""mask
print(Block("object",
                Block("difference",
                      Box("W", #W == wall
                          mdv.cell[0]*-100+mdv.cell[1]*-100+np.array([0,0,0]),
                          mdv.cell[0]*100+mdv.cell[1]*100+np.array([0,0,1]))+
                      Box("W",
                          mdv.cell[0]*0+mdv.cell[1]*0+np.array([0,0,-1]),
                          mdv.cell[0]*1+mdv.cell[1]*1+np.array([0,0,2]))) + Block( "material", "MATW" ) + " no_shadow"))
"""

