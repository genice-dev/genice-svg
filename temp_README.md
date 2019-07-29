<img src="4R.png">

    genice 4R -f png[shadow:rotatex=2:rotatey=88] > 4R.png


# [genice-svg](%%url%%)

A [GenIce](https://github.com/vitroid/GenIce) plugin to illustrate the structure in SVG (and PNG) format.

version %%version%%

## Requirements

* %%requires%%

* [GenIce](https://github.com/vitroid/GenIce) >=0.23.
* svgwrite.
* Pillow.

## Installation from PyPI

    % pip install %%package%%

## Manual Installation

### System-wide installation

    % make install

### Private installation

Copy the files in genice_svg/formats/ into your local formats/ folder.

## Usage

    %%usage_svg%%

Png is a quick alternative for svg. Use png if making svg is too slow.

    %%usage_png%%

## Test in place

    % make test
