"""Draws crystal shapes other than the diamond one and colours them per material (graphics only, the mod is not changed).

Shapes are 16x16 templates in 6 greys, 1 (outline) to 6 (highlight); grey n becomes the n-th colour
(dark to light) of the material's 6-colour palette from generate.py. The templates in art\\crystal shapes\\templates
are the user's (edited in Aseprite); they are read, never overwritten. The drawing code below only makes a missing one.
Output: art\\crystal shapes\\ (templates, one PNG per crystal, preview.png).
Run:  python crystal_shapes.py
"""
import math
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate as g  # noqa: E402  (material list, palettes, vanilla textures)

OUT = os.path.join(g.MOD, "art", "crystal shapes")

SHAPES = g.SHAPES


def cabochon():
    """Smooth oval dome lit from the top left."""
    cx, cy, rx, ry = 7.5, 7.5, 5.2, 6.9
    inside = {(x, y) for y in range(16) for x in range(16) if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0}
    light = (-0.45, -0.6, 0.66)
    norm = math.sqrt(sum(v * v for v in light))
    light = tuple(v / norm for v in light)
    t = [[0] * 16 for _ in range(16)]
    for x, y in inside:
        if any((x + dx, y + dy) not in inside for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            t[y][x] = 1
            continue
        nx, ny = (x - cx) / (rx + 0.6), (y - cy) / (ry + 0.6)
        nz = math.sqrt(max(0.0, 1 - nx * nx - ny * ny))
        i = nx * light[0] + ny * light[1] + nz * light[2]
        t[y][x] = 2 if i < 0.35 else 3 if i < 0.62 else 4 if i < 0.84 else 5
    # small glint on the upper left of the dome
    for x, y in ((5, 4), (6, 4), (5, 5)):
        if t[y][x] > 1:
            t[y][x] = 6
    return t


def step():
    """Emerald (step) cut: rectangle with cut corners and two rings of facets around a flat table."""
    x0, x1, y0, y1, cut = 3, 12, 1, 14, 2
    t = [[0] * 16 for _ in range(16)]

    def ring(x, y):
        """How many pixels inside the outline; -1 outside."""
        if not (x0 <= x <= x1 and y0 <= y <= y1):
            return -1
        d = min(x - x0, x1 - x, y - y0, y1 - y)
        corner = min(x - x0, x1 - x) + min(y - y0, y1 - y)
        if corner < cut:
            return -1
        return min(d, corner - cut)

    for y in range(16):
        for x in range(16):
            r = ring(x, y)
            if r < 0:
                continue
            if r == 0:
                t[y][x] = 1
            elif r >= 3:
                t[y][x] = 4  # table
            else:
                top, bottom, left, right = y - y0, y1 - y, x - x0, x1 - x
                side = min((top, "top"), (bottom, "bottom"), (left, "left"), (right, "right"))[1]
                shade = {"top": 5, "left": 4, "right": 3, "bottom": 2}[side]
                t[y][x] = shade if r == 1 else max(2, shade - 1)
    # light streak across the table
    for x, y in ((6, 5), (7, 6), (6, 6), (8, 7)):
        if t[y][x] == 4:
            t[y][x] = 5
    t[4][6] = 6
    return t


def to_image(template, colours):
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    for y in range(16):
        for x in range(16):
            s = template[y][x]
            if s:
                img.putpixel((x, y), colours[s - 1] + (255,))
    return img


GREY = [(30, 30, 34), (70, 70, 76), (110, 110, 116), (150, 150, 156), (195, 195, 200), (245, 245, 248)]


def read_template(path):
    """The user's template: each grey becomes its shade number (nearest of the 6 greys)."""
    img = Image.open(path).convert("RGBA")
    t = [[0] * 16 for _ in range(16)]
    for y in range(16):
        for x in range(16):
            r, gr, b, a = img.getpixel((x, y))
            if a:
                t[y][x] = 1 + min(range(6), key=lambda i: sum((c - d) ** 2 for c, d in zip((r, gr, b), GREY[i])))
    return t


def main():
    os.makedirs(os.path.join(OUT, "templates"), exist_ok=True)
    templates = {}
    for name, draw_default in (("cabochon", cabochon), ("step", step)):
        path = os.path.join(OUT, "templates", f"{name}.png")
        if not os.path.exists(path):  # never overwrite a template the user edited
            to_image(draw_default(), GREY).save(path)
        templates[name] = read_template(path)

    by_name = {m.name: m for m in g.MATS}
    rows = []
    for shape, names in SHAPES.items():
        for n in names:
            m = by_name[n]
            img = to_image(templates[shape], g.ramp(m.coin))
            img.save(os.path.join(OUT, f"{m.coin:03} {n}.png"))
            old = os.path.join(g.ASSETS, "textures", "item", f"{n}.png")
            rows.append((m, shape, Image.open(old).convert("RGBA") if os.path.exists(old) else None, img))
    rows.sort(key=lambda r: r[0].coin)

    cell, label = 64, 190
    sheet = Image.new("RGBA", (label + cell * 3 + 20, cell * (len(rows) + 1)), (40, 40, 48, 255))
    draw = ImageDraw.Draw(sheet)
    for i, head in enumerate(("coin", "now", "new")):
        draw.text((label + i * cell + 8, 24), head, fill=(200, 200, 200, 255))
    for row, (m, shape, old, new) in enumerate(rows):
        y = (row + 1) * cell
        draw.text((6, y + 26), f"{m.coin:2} {m.label} ({shape})", fill=(230, 230, 230, 255))
        coin = g.coin_image(m.coin, True)
        for i, im in enumerate((coin, old, new)):
            if im is not None:
                sheet.alpha_composite(im.resize((cell - 8, cell - 8), Image.NEAREST), (label + i * cell + 4, y + 4))
    sheet.save(os.path.join(OUT, "preview.png"))
    print(len(rows), "crystals drawn")


if __name__ == "__main__":
    main()
