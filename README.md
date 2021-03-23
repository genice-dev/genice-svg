<img src="4R.png">

    genice2 4R -f png[shadow:rotatex=2:rotatey=88] > 4R.png


# [genice2-svg](https://github.com/vitroid/genice-svg/)

A [GenIce2](https://github.com/vitroid/GenIce) plugin to illustrate the structure in SVG (and PNG) format.

version 2.1

## Requirements


* svgwrite
* genice2>=2.1b0
* pillow
* cycless

## Installation from PyPI

```shell
% pip install genice2-svg
```

## Manual Installation

### System-wide installation

```shell
% make install
```

### Private installation

Copy the files in genice2_svg/formats/ into your local formats/ folder.

## Usage
        
    Usage:
        % genice CS2 -r 3 3 3 -f svg[rotatex=30:shadow] > CS2.svg

    Options:
        rotatex=30
        rotatey=30
        rotatez=30
        polygon        Draw polygons instead of a ball and stick model.
        arrows         Draw the hydrogen bonds with arrows.
        shadow=#8881   Draw shadows behind balls.
        bg=#f00        Specify the background color.
        O=0.06
        H=0            Size of the hydrogen atom (relative to that of oxygen)
        HB=0.4         Radius of HB relative to that of oxygem
        OH=0.5         Radius of OH colvalent bond relative to that of oxygem
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
        H=0            Size of the hydrogen atom (relative to that of oxygen)
        O=0.06         Size of the oxygen atom in nm.
        HB=0.4         Radius of HB relative to that of oxygen
        OH=0.5         Radius of OH colvalent bond relative to that of oxygen
        width=0        (Pixel)
        height=0       (Pixel)

## Test in place

```shell
% make test
```
