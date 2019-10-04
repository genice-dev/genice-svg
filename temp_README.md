<img src="4R.png">

    genice 4R -f png[shadow:rotatex=2:rotatey=88] > 4R.png


# [genice-svg]({{url}})

A [GenIce](https://github.com/vitroid/GenIce) plugin to illustrate the structure in SVG (and PNG) format.

version {{version}}

## Requirements
{% for i in requires %}
* {{i}}
{%- endfor %}

## Installation from PyPI

    % pip install {{package}}

## Manual Installation

### System-wide installation

    % make install

### Private installation

Copy the files in genice_svg/formats/ into your local formats/ folder.

## Usage

{%- filter indent %}
    {{usage_svg}}
{%- endfilter %}

Png is a quick alternative for svg. Use png if making svg is too slow.

{%- filter indent %}
    {{usage_png}}
{%- endfilter %}

## Test in place

    % make test
