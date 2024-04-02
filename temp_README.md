{% include '4R.svg' %}

```shell
genice2 4R -f svg[shadow:rotatex=2:rotatey=88] > 4R.svg
```

![Logo]({{tool.genice.urls.logo}})


# [{{project.name}}]({{project.urls.Homepage}})

A [GenIce2]({{tool.genice.urls.repository}}) plugin to illustrate the structure in SVG (and PNG) format.

version {{version}}

## Requirements

{% for item in tool.poetry.dependencies %}* {{item}}{{tool.poetry.dependencies[item]}}
{% endfor %}

## Installation from PyPI

```shell
% pip install {{project.name}}
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
