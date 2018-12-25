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
            line = self.file.readline()
            natom = int(line)
            atoms = defaultdict(list)
            for i in range(natom):
                line = self.file.readline()
                cols = line.split()
                atomname = cols[0]
                if atomname == "Od":
                    atomname = "Ow"
                elif atomname == "Oa":
                    atomname = "Os"
                pos = np.array([float(x) for x in cols[1:4]]) * au
                #pos[1] -= 0.3 # small slide 3 AA
                #pos = np.dot(pos,celli) #to relative
                #pos -= np.floor(pos) # wrap
                atoms[atomname].append(pos)
            carbons = np.array(atoms['C'])
            czmin = np.min(carbons[:,2]) - 1
            czmax = np.max(carbons[:,2]) + 1
            logger.info(czmin)
            logger.info(czmax)
            self.cell[2,2] = czmax - czmin
            celli = np.linalg.inv(self.cell)
            for atom in atoms:
                a = np.array(atoms[atom])
                A = a[:,2] > czmin
                B = a[:,2] < czmax
                C = A & B
                a = a[C,:]
                a[:,2] -= czmin
                atoms[atom] = np.dot(a, celli)
            yield atoms
            del atoms

def Carbons(c, cell):
    prims = []
    # Carbon
    grid200 = pl.determine_grid(cell, 0.200)
    CNT = nx.Graph([(i,j) for i,j in pl.pairs_fine(np.array(c), 0.2, cell, grid200, distance=False)])
    for ring in cr.CountRings(CNT).rings_iter(6):
        if len(ring) != 6:
            continue
        v = np.zeros((6,3))
        for i,j in enumerate(ring):
            v[i] = atoms['C'][j]
        ori = v[0].copy()
        v -= ori
        v -= np.floor( v + 0.5 )
        com = np.sum(v, axis=0) / 6. #rel
        v -= com                     #rel
        com += ori                   #abs
        prims.append([np.dot(com, projected), "P", np.dot(v, projected),
                      {"fill":"#fff", "fill_opacity": 0.85, "stroke":"#00f", "stroke_width":2}])
    return prims

            
logging.basicConfig(level=logging.INFO,
                    format="%(levelname)s %(message)s")
logger = logging.getLogger()

proj = np.array(([0.0, 1.0, 0.0], [0.25, 0.0, (1.0 - 0.25**2)**0.5], [1.0, 0.0, 0.0]))
drawOw = True
name = "y"
if len(sys.argv) > 1 and sys.argv[1] == "Z":
    drawOw = False
    proj = np.array(([0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, 0.0, 1.0]))
    name = "z"
if len(sys.argv) > 1 and sys.argv[1] == "X":
    drawOw = True
    proj = np.array(([0.0, 0.0,-1.0], [0.0, 1.0, 0.0], [1.0, 0.0, 0.0]))
    name = "x"
logger.info(np.linalg.det(proj))
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
    projected = np.dot(mdv.cell, proj)
    prims = []

    origin = np.zeros(3)
    # origin[2] = 56*0.052917721067-1

    trim = mdv.cell.copy()
    # trim[2,2] = 170*0.052917721067+1 - origin[2]

    origin = np.dot(origin, proj)
    trim = np.dot(trim, proj)
    xmin, xmax, ymin, ymax = svg.draw_cell(prims, trim, stroke_width=0)

    if True:
        prims += Carbons(atoms['C'], mdv.cell)
    
#    for i,j in CNT.edges():
#        vi = atoms['C'][i]
#        vj = atoms['C'][j]
#        dv = vj - vi
#        dv -= np.floor( dv + 0.5 )
#        vj = vi + dv
#        vc = vi + dv / 2
#        prims.append([np.dot(vc, projected), "L", np.dot(vj, projected), np.dot(vi, projected), 0, {"stroke_width":1, "stroke":"#000"}])
    # mobile water and HBs
    grid300 = pl.determine_grid(mdv.cell, 0.300)
    if drawOw:
        for i,j,d in pl.pairs_fine(np.array(atoms['Ow']), 0.3, mdv.cell, grid300, distance=True):
            vi = atoms['Ow'][i]
            vj = atoms['Ow'][j]
            dv = vj - vi
            dv -= np.floor( dv + 0.5 )
            vj = vi + dv
            vc = vi + dv / 2
            prims.append([np.dot(vc, projected), "L", np.dot(vj, projected), np.dot(vi, projected), 0, {"stroke_width":1, "stroke":"#ccc"}])  #light green #4db
    # immobile water and HBs
    if len(atoms['Os']) > 0:
        for i,j,d in pl.pairs_fine(np.array(atoms['Os']), 0.3, mdv.cell, grid300, distance=True):
            vi = atoms['Os'][i]
            vj = atoms['Os'][j]
            dv = vj - vi
            dv -= np.floor( dv + 0.5 )
            vj = vi + dv
            vc = vi + dv / 2
            prims.append([np.dot(vc, projected), "L", np.dot(vj, projected), np.dot(vi, projected), 0, {"stroke_width":3, "stroke":"#000" }])
        for i,j,d in pl.pairs_fine_hetero(np.array(atoms['Os']), np.array(atoms['Ow']), 0.3, mdv.cell, grid300, distance=True):
            vi = atoms['Os'][i]
            vj = atoms['Ow'][j]
            dv = vj - vi
            dv -= np.floor( dv + 0.5 )
            vj = vi + dv
            vc = vi + dv / 2
            prims.append([np.dot(vc, projected), "L", np.dot(vj, projected), np.dot(vi, projected), 0, {"stroke_width":2, "stroke":"#888"}]) #286 dark green
    Rsphere = 0.02
    #for c in atoms["C"]:
    #    prims.append([np.dot(c, projected), "C", Rsphere, {}])
    s = svg.Render(prims, Rsphere, shadow=False,
                      topleft=np.array((xmin, ymin)),
                      size=(xmax-xmin, ymax-ymin))
    #    with open(outfilename, "w") as file:
    #        file.write(s)

    # for single file
    print(s)

    

    
