"""Gallery pictures for CurseForge (permanent tool; run again after textures change):
- Nekoro Gear\\art\\gallery\\all-colours.png  every colour in one row: coins, bags, materials, blocks, tools, armor
  (the same picture goes to Gear, Coins, Collector Edition and Random Drop)
- Nekoro Gear\\art\\gallery\\gear.png         one row per kind of item, one column per colour
- Nekoro Coins\\art\\gallery\\coins.png        the 120 coins in 3 rows; coins.gif: coin 1 to 120, 10x size
- Nekoro Collector Edition\\art\\gallery\\bags.png  the 120 bags in 3 rows
Run:  python gallery.py
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate as g  # noqa: E402

MODS = os.path.dirname(g.MOD)
COINS = os.path.join(MODS, "Nekoro Coins", "art", "coins")
BAGS = os.path.join(MODS, "Nekoro Collector Edition", "art", "items")
BG = (34, 34, 42, 255)
STRIPE = (42, 42, 52, 255)
TEXT = (235, 235, 240, 255)
HEAD = (185, 106, 217, 255)  # the purple of the descriptions
FONT = ImageFont.truetype("arialbd.ttf", 22)
SMALL = ImageFont.truetype("arialbd.ttf", 17)


def coin(k):
    return Image.open(os.path.join(COINS, f"{k}.png")).convert("RGBA")


def bag(k):
    return Image.open(os.path.join(BAGS, f"bag{k:03}.png")).convert("RGBA")


def own(rel):
    p = os.path.join(g.ASSETS, "textures", rel + ".png")
    return Image.open(p).convert("RGBA") if os.path.exists(p) else None


def van(rel):
    try:
        return g.vanilla(rel)
    except KeyError:
        return None


def first_frame(im):
    return im.crop((0, 0, im.width, im.width)) if im is not None else None


def put(canvas, im, x, y, size):
    if im is None:
        return
    im = first_frame(im).resize((size, size), Image.NEAREST)
    canvas.alpha_composite(im, (x, y))


def materials(m):
    """material, piece, raw, block, ore, deepslate ore"""
    n = m.name
    if m.kind == "C":
        return [own(f"item/{n}"), own(f"item/{n}_shard"), None, own(f"block/{n}_block"), own(f"block/{n}_ore"),
                own(f"block/deepslate_{n}_ore")]
    if m.kind == "M":
        return [own(f"item/{n}_ingot"), own(f"item/{n}_nugget"), own(f"item/raw_{n}"), own(f"block/{n}_block"),
                own(f"block/{n}_ore"), own(f"block/deepslate_{n}_ore")]
    if m.kind == "A":
        return [own(f"item/{n}_ingot"), own(f"item/{n}_nugget"), None, own(f"block/{n}_block"), None, None]
    v = g.VANILLA_ITEMS.get(n, [None] * 7)
    pick = [v[0], v[1], v[2], v[3], v[5], v[6]]
    return [(own(p[4:]) if p and p.startswith("own:") else van(p)) if p else None for p in pick]


def blocks(m):
    n = m.name
    return [own(f"block/large_{n}_bricks"), own(f"block/small_{n}_bricks"), own(f"block/smooth_{n}"),
            own(f"block/{n}_pillar"), own(f"block/{n}_lamp"), own(f"block/{n}_redstone_lamp_on")]


def gear(m):
    if m.tools:
        return [own(f"item/{m.name}_{t}") for t in g.TOOLS + g.ARMOR]
    vname = {"gold": "golden"}.get(m.name, m.name)
    return [van(f"item/{vname}_{t}") for t in g.TOOLS + g.ARMOR]


def all_colours(path):
    groups = [("Coins", 3), ("Bags", 3), ("Materials", 6), ("Blocks", 6), ("Tools", 5), ("Armor", 4)]
    cell, gap, label, top = 68, 22, 230, 58
    width = label + sum(n for _, n in groups) * cell + gap * (len(groups) - 1) + 12
    img = Image.new("RGBA", (width, top + 40 * cell + 10), BG)
    d = ImageDraw.Draw(img)
    x = label
    for name, n in groups:
        d.text((x + 4, 18), name, font=FONT, fill=HEAD)
        x += n * cell + gap
    for row, m in enumerate(g.MATS):
        y = top + row * cell
        if row % 2:
            d.rectangle((0, y, width, y + cell - 1), fill=STRIPE)
        d.text((12, y + 21), f"{m.coin:03}  {m.label}", font=FONT, fill=TEXT)
        k = m.coin
        items = [[coin(k), coin(k + 40), coin(k + 80)], [bag(k), bag(k + 40), bag(k + 80)], materials(m), blocks(m)]
        g_items = gear(m)
        items += [g_items[:5], g_items[5:]]
        x = label
        for group in items:
            for im in group:
                put(img, im, x + 2, y + 2, cell - 4)
                x += cell
            x += gap
    img.save(path)


def by_kind(path):
    """Nekoro Gear: rows of item kinds, columns of colours."""
    rows = [("Material", lambda m: materials(m)[0]), ("Piece", lambda m: materials(m)[1]),
            ("Block", lambda m: materials(m)[3]), ("Ore", lambda m: materials(m)[4]),
            ("Large bricks", lambda m: blocks(m)[0]), ("Small bricks", lambda m: blocks(m)[1]),
            ("Smooth", lambda m: blocks(m)[2]), ("Pillar", lambda m: blocks(m)[3]),
            ("Lamp", lambda m: blocks(m)[4]), ("Redstone lamp", lambda m: blocks(m)[5])]
    rows += [(t.capitalize(), (lambda i: lambda m: gear(m)[i])(i)) for i, t in enumerate(g.TOOLS + g.ARMOR)]
    cell, label = 52, 190
    img = Image.new("RGBA", (label + 40 * cell + 10, len(rows) * cell + 10), BG)
    d = ImageDraw.Draw(img)
    for r, (name, get) in enumerate(rows):
        y = 5 + r * cell
        if r % 2:
            d.rectangle((0, y, img.width, y + cell - 1), fill=STRIPE)
        d.text((12, y + 15), name, font=SMALL, fill=TEXT)
        for c, m in enumerate(g.MATS):
            put(img, get(m), label + c * cell + 2, y + 2, cell - 4)
    img.save(path)


def strip(path, load):
    """120 pictures in 3 rows of 40."""
    cell = 64
    img = Image.new("RGBA", (40 * cell + 20, 3 * cell + 20), BG)
    for k in range(1, 121):
        put(img, load(k), 10 + (k - 1) % 40 * cell + 2, 10 + (k - 1) // 40 * cell + 2, cell - 4)
    img.save(path)


def gif(path, load, scale=10, ms=100):
    """Transparent GIF of pictures 1-120, like the bag GIFs (index 0 is transparent)."""
    frames = []
    for k in range(1, 121):
        im = load(k)
        im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
        rgb = im.convert("RGB").quantize(colors=255)
        pal = rgb.getpalette()[:255 * 3]
        out = Image.new("P", im.size, 0)
        out.putpalette([0, 0, 0] + pal + [0, 0, 0] * (256 - 256))
        alpha = im.getchannel("A").load()
        src = rgb.load()
        dst = out.load()
        for y in range(im.height):
            for x in range(im.width):
                if alpha[x, y] > 127:
                    dst[x, y] = src[x, y] + 1
        frames.append(out)
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=ms, loop=0, transparency=0, disposal=2,
                   optimize=False)


if __name__ == "__main__":
    gear_dir = os.path.join(g.MOD, "art", "gallery")
    coins_dir = os.path.join(MODS, "Nekoro Coins", "art", "gallery")
    bags_dir = os.path.join(MODS, "Nekoro Collector Edition", "art", "gallery")
    for p in (gear_dir, coins_dir, bags_dir):
        os.makedirs(p, exist_ok=True)
    all_colours(os.path.join(gear_dir, "all-colours.png"))
    by_kind(os.path.join(gear_dir, "gear.png"))
    strip(os.path.join(coins_dir, "coins.png"), coin)
    strip(os.path.join(bags_dir, "bags.png"), bag)
    gif(os.path.join(coins_dir, "coins.gif"), coin)
    print("done")
