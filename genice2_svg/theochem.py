from collections import defaultdict

import numpy as np
import networkx as nx
import sys
from attrdict import AttrDict
from logging import getLogger
from genice_svg import hooks, render_svg

from countrings import countrings_nx as cr

v1 = np.array([0.0, 0.0, 0.0])
r1 = 0.75
v2 = np.array([1.0, 1.0, 1.0])
r2 = 0.5
rb = 0.25

prims = []
prims.append(hooks.clip_cyl(v1, r1, v2, r2, rb) + [rb, {}])
prims.append([v1, "C", r1, {}])
prims.append([v2, "C", r2, {}])
render_svg.Render(prims, r1)
