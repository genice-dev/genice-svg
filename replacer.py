#!/usr/bin/env python
import sys
from genice_svg.formats.svg import __doc__ as doc_svg
from genice_svg.formats.png import __doc__ as doc_png
import distutils.core
import jinja2 as jj

setup = distutils.core.run_setup("setup.py")

d = {
    "usage_svg"   : "\n".join(doc_svg.splitlines()[2:]),
    "usage_png"   : "\n".join(doc_png.splitlines()[2:]),
    "version" : setup.get_version(),
    "package" : setup.get_name(),
    "url"     : setup.get_url(),
    "genice"  : "[GenIce](https://github.com/vitroid/GenIce)",
    "requires": setup.install_requires,
}


print(jj.Template(sys.stdin.read()).render(d))
