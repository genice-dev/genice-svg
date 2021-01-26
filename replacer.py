#!/usr/bin/env python
from genice2_dev import template

import sys
from genice2_svg.formats.svg import __doc__ as doc_svg
from genice2_svg.formats.png import __doc__ as doc_png
import distutils.core

setup = distutils.core.run_setup("setup.py")

d = {
    "usage_svg"   : "\n".join(doc_svg.splitlines()[2:]),
    "usage_png"   : "\n".join(doc_png.splitlines()[2:]),
}

print(template(sys.stdin.read(), doc_svg, setup, add=d))
