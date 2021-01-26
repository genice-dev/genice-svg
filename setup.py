#!/usr/bin/env python

# from distutils.core import setup, Extension
from setuptools import setup, Extension, find_packages
import os
import codecs
import re

#Copied from wheel package
here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(os.path.dirname(__file__), 'genice2_svg', '__init__.py'),
                 encoding='utf8') as version_file:
    metadata = dict(re.findall(r"""__([a-z]+)__ = "([^"]+)""", version_file.read()))

long_desc = "".join(open("README.md").readlines())

setup(
    name='genice2-svg', # the package name
    version=metadata['version'],
    description='SVG format plugin for GenIce.',
    long_description=long_desc,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
    ],
    author='Masakazu Matsumoto',
    author_email='vitroid@gmail.com',
    url='https://github.com/vitroid/genice-svg/',
    keywords=['genice', 'SVG'],

    packages=find_packages(),

    entry_points = {
        'genice2_format': [
            'svg = genice2_svg.formats.svg',
            'png = genice2_svg.formats.png',
        ],
    },
    install_requires=['svgwrite', 'genice2', 'pillow',
                      'cycless'],

    license='MIT',
)
