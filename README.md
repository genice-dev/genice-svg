<img src="4R.png">

    genice 4R -f png[shadow:rotatex=2:rotatey=88] > 4R.png


# genice-svg

A [GenIce](https://github.com/vitroid/GenIce) plugin to illustrate the structure in SVG (and PNG) format.

## Requirements

* [GenIce](https://github.com/vitroid/GenIce) >=0.23.
* svgwrite.
* Pillow.

## Installation from PyPI

    % pip install genice-svg

## Manual Installation

### System-wide installation

    % make install

### Private installation

Copy the files in genice_svg/formats/ into your local formats folder of GenIce.

## Usage

	% genice CS2 -r 3 3 3 -f svg[options:separated:by:colons] > CS2.svg
	
	Options:
        rotatex=30
        rotatey=30
        rotatez=30
		polygon        Draw polygons instead of a ball and stick model.
		shadow         Draw shadows behind balls.
		bg=#f00        Specify the background color.

Png is a quick alternative for svg. Use png if making svg is too slow.

	% genice CS2 -r 3 3 3 -f png[options:separated:by:colons] > CS2.png
	
	Options:
        rotatex=30
        rotatey=30
        rotatez=30
		shadow         Draw shadows behind balls.
		bg=#f00        Specify the background color.


## Test in place

    % make test
