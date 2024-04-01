#!/usr/bin/env python
from jinja2 import Template, BaseLoader, Environment, FileSystemLoader
import toml
import genice2_svg

import sys
from genice2_svg.formats.svg import __doc__ as doc_svg
from genice2_svg.formats.png import __doc__ as doc_png

project = toml.load("pyproject.toml")

project |= {
    "usage_svg": "\n".join(doc_svg.splitlines()[2:]),
    "usage_png": "\n".join(doc_png.splitlines()[2:]),
    "version": genice2_svg.__version__,
}

t = Environment(loader=FileSystemLoader(searchpath=".")).get_template(sys.argv[1])
markdown_en = t.render(**project)
print(markdown_en)
