<img src="4R.png">

    genice2 4R -f png[shadow:rotatex=2:rotatey=88] > 4R.png


# [{{package}}]({{url}})

A {{genice}} plugin to illustrate the structure in SVG (and PNG) format.

version {{version}}

## Requirements

{% for i in requires %}
* {{i}}
{%- endfor %}

## Installation from PyPI

```shell
% pip install {{package}}
```

## Manual Installation

### System-wide installation

```shell
% make install
```

### Private installation

Copy the files in {{base}}/formats/ into your local formats/ folder.

## Usage

{%- filter indent %}
    {{usage_svg}}
{%- endfilter %}

Png is a quick alternative for svg. Use png if making svg is too slow.

{%- filter indent %}
    {{usage_png}}
{%- endfilter %}

## Test in place

```shell
% make test
```
