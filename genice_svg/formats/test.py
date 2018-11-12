import svgwrite

def oval(R, ratio, kwargs):
    # https://stackoverflow.com/questions/1734745/how-to-create-circle-with-b%C3%A9zier-curves
    magic = 0.552284749831
    x1 = R
    x2 = x1*magic
    y1 = ratio*R
    y2 = y1*magic
    p = []
    p.append(["M", x1, 0])
    p.append(["C", x1, y2, x2, y1,  0, y1])
    p.append(["C",-x2, y1,-x1, y2,-x1, 0])
    p.append(["C",-x1,-y2,-x2,-y1,  0,-y1])
    p.append(["C", x2,-y1, x1,-y2, x1, 0])
    p.append(["Z"])
    return svgwrite.path.Path(d=p, **kwargs)

def cylinder_path(R, ratio, L, **kwargs):
    magic = 0.552284749831
    x1 = R
    x2 = x1*magic
    y1 = ratio*R
    y2 = y1*magic
    p = []
    p.append(["M", x1, 0])
    p.append(["L", x1, L])
    p.append(["C", x1, y2+L, x2, y1+L,  0, y1+L])
    p.append(["C",-x2, y1+L,-x1, y2+L,-x1, 0+L])
    p.append(["L",-x1, 0])
    p.append(["C",-x1,-y2,-x2,-y1,  0,-y1])
    p.append(["C", x2,-y1, x1,-y2, x1, 0])
    p.append(["Z"])
    return svgwrite.path.Path(d=p, **kwargs)
    

svg = svgwrite.Drawing()
svg.add(cylinder_path(100,0.5,40, stroke='red', stroke_width='5'))
#svg.add(oval(100,0.5).translate(100,100))
print(svg.tostring())

