<img src="4R.png">

    genice 4R -f png[shadow:rotatex=2:rotatey=88] > 4R.png


# [genice-svg](https://github.com/vitroid/genice-svg/)

A [GenIce](https://github.com/vitroid/GenIce) plugin to illustrate the structure in SVG (and PNG) format.

version 0.5

## Requirements

* svgwrite
* genice>=0.25
* pillow
* attrdict
* countrings>=0.1.7

## Installation from PyPI

    % pip install genice_svg

## Manual Installation

### System-wide installation

    % make install

### Private installation

Copy the files in genice_svg/formats/ into your local formats/ folder.

## Usage
        
    Usage:
        % genice CS2 -r 3 3 3 -f svg[rotatex=30:shadow] > CS2.svg
    	
    Options:
        rotatex=30
        rotatey=30
        rotatez=30
        polygon        Draw polygons instead of a ball and stick model.
        shadow         Draw shadows behind balls.
        bg=#f00        Specify the background color.
        H=0            Size of the hydrogen atom
        O=0.06
        HB=0.4
        OH=0.5
        width=0        (Pixel)
        height=0       (Pixel)

Png is a quick alternative for svg. Use png if making svg is too slow.
        
    Usage:
        % genice CS2 -r 3 3 3 -f png[shadow:bg=#f00] > CS2.png
    	
    Options:
        rotatex=30
        rotatey=30
        rotatez=30
        shadow         Draw shadows behind balls.
        bg=#f00        Specify the background color.
        H=0            Size of the hydrogen atom
        O=0.06
        HB=0.4
        OH=0.5
        width=0        (Pixel)
        height=0       (Pixel)

## Test in place

    % make test
