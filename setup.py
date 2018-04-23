#!/usr/bin/env python

# from distutils.core import setup, Extension
from setuptools import setup, Extension
from numpy.distutils.misc_util import get_numpy_include_dirs
import os
import codecs
import re

#Copied from wheel package
here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(os.path.dirname(__file__), 'svg.py'),
                 encoding='utf8') as version_file:
    metadata = dict(re.findall(r"""__([a-z]+)__ = "([^"]+)""", version_file.read()))
    

setup(
    name='genice_svg',
    version=metadata['version'],
    description='SVG format pluing for GenIce.',
    #long_description=README + '\n\n' +  CHANGES,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
    ],
    author='Masakazu Matsumoto',
    author_email='vitroid@gmail.com',
    url='https://github.com/vitroid/genice-svg/',
    keywords=['genice', 'SVG'],

    py_modules=['svg', 'svg_poly'],
    # packages=['formats', ],
    
    entry_points = {
        'genice_format_hook2': [
            'svg      = svg:hook2',
        ],
        'genice_format_hook4': [
            'svg_poly = svg_poly:hook4',
        ]
    },
    install_requires=['svgwrite', 'numpy'],

    license='MIT',
)
