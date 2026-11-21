"""Generates everything of Nekoro Gear that follows from the material list:
GearMaterials.java, textures (vanilla textures recoloured with the coin palettes), models, blockstates, lang,
recipes, loot tables, tags, ore worldgen, and art\\preview.png.

Run from anywhere:  python generate.py
Textures are recoloured from the Minecraft 1.21.1 jar and the coin textures of Nekoro Coins (colours 1-40).
Hand-drawn textures can later replace the generated ones: list them in KEEP so they are not overwritten.
"""
import colorsys
import io
import json
import os
import shutil
import zipfile

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.dirname(HERE)
MOD = os.path.dirname(SOURCE)
RES = os.path.join(SOURCE, "common", "resources")
ASSETS = os.path.join(RES, "assets", "nekorogear")
DATA = os.path.join(RES, "data")
JAVA = os.path.join(SOURCE, "common", "java-core", "dev", "xardas", "nekorogear", "GearMaterials.java")
JAR = r"E:\Minecraft\Install\versions\1.21.1\1.21.1.jar"
# The user's original coins and bags 1-40 as drawn (copies; the Coins and Collector Edition mods use the corrected
# colours since 2026-11-20, so the colour shifts must start from these originals).
ORIGINALS = os.path.join(MOD, "art", "coins and bags")


def original(coin, kind):
    return os.path.join(ORIGINALS, f"{coin:03} {kind}.png")
ICON = r"E:\Minecraft\Mods\Nekoro Collector Edition\source\common\resources\assets\nekorocollectoredition\textures\item\nekoro_icon.png"
NS = "nekorogear"

# Texture files (relative to assets/nekorogear/textures) drawn by hand; the generator leaves them alone.
KEEP = set()

# Crystal shapes other than the diamond one: the user's 6-grey templates in art\crystal shapes\templates
# (grey 1 outline ... 6 highlight becomes the material's colour 1 ... 6).
SHAPES = {
    "cabochon": ["jade", "jasper", "epidote", "aventurine", "chrysoprase", "amazonite", "chrysocolla",
                 "lepidolite", "sugilite", "rhodochrosite", "onyx", "carnelian"],
    "step": ["aquamarine", "kunzite", "fluorite"],
}
SHAPE_GREYS = [(30, 30, 34), (70, 70, 76), (110, 110, 116), (150, 150, 156), (195, 195, 200), (245, 245, 248)]

# Alloys: crafted from these ingots (shapeless, 3 + 1 -> 4); they have no raw form and no ore.
ALLOYS = {"bronze": ["minecraft:copper_ingot"] * 3 + ["nekorogear:tin_ingot"],
          "tumbaga": ["minecraft:copper_ingot"] * 3 + ["minecraft:gold_ingot"]}

# Colours whose material IS a vanilla one get that material's exact colours (the coins were picked by hand).
# Colours that got a new material (Topaz, Spinel, Aquamarine...) keep the user's coin colours.
CORRECT = {
    2: "item/redstone", 6: "item/copper_ingot", 10: "item/gold_ingot", 16: "item/emerald", 21: "item/diamond",
    26: "item/lapis_lazuli", 31: "item/amethyst_shard", 36: "item/iron_ingot", 40: "item/netherite_ingot",
}

# Colours moved to fit their Pokémon type (modern type colours) or to stand apart from neighbours
# (accepted 2026-11-20): the coin's 6 colours are shifted so the main one (4th) becomes this one.
TARGET = {
    13: "#a6c41c",  # Bug: yellow-green
    23: "#81b9ef",  # Flying: light sky blue
    24: "#2f7fe8",  # Water: fuller blue
    25: "#5a4de0",  # Dragon: violet-blue
    32: "#f04f84",  # Psychic: stronger pink
    34: "#8cdcf3",  # Ice: icy cyan
    35: "#e9ecef",  # Stellar: neutral white
    37: "#aba384",  # Rock: warm grey-beige
    38: "#5d4f57",  # Dark: dark grey with a warm tint
}

# coin, name, kind (C crystal, M metal, A alloy, V vanilla), level (W weak, S stone, I iron, D diamond, None = has tools),
# metal look, repair/crafting item for vanilla materials, extra item for vanilla materials
MATERIALS = [
    (1, "ruby", "C", "D", False, None, None),
    (2, "redstone", "V", "W", False, "minecraft:redstone", None),
    (3, "garnet", "C", "I", False, None, None),
    (4, "bronze", "A", "I", True, None, None),
    (5, "jasper", "C", "S", False, None, None),
    (6, "copper", "V", "S", True, "minecraft:copper_ingot", "copper_nugget"),
    (7, "carnelian", "C", "I", False, None, None),
    (8, "tumbaga", "A", "I", True, None, None),
    (9, "citrine", "C", "I", False, None, None),
    (10, "gold", "V", None, True, None, None),
    (11, "topaz", "C", "I", False, None, None),
    (12, "peridot", "C", "I", False, None, None),
    (13, "jade", "C", "I", False, None, None),
    (14, "epidote", "C", "S", False, None, None),
    (15, "aventurine", "C", "S", False, None, None),
    (16, "emerald", "V", "D", False, "minecraft:emerald", None),
    (17, "chrysoprase", "C", "S", False, None, None),
    (18, "amazonite", "C", "I", False, None, None),
    (19, "mithril", "M", "D", True, None, None),
    (20, "chrysocolla", "C", "I", False, None, None),
    (21, "diamond", "V", None, False, None, None),
    (22, "fluorite", "C", "I", False, None, None),
    (23, "celestine", "C", "I", False, None, None),
    (24, "sapphire", "C", "D", False, None, None),
    (25, "cobalt", "M", "D", True, None, None),
    (26, "lapis", "V", "W", False, "minecraft:lapis_lazuli", None),
    (27, "lepidolite", "C", "I", False, None, None),
    (28, "spinel", "C", "I", False, None, None),
    (29, "tanzanite", "C", "D", False, None, None),
    (30, "sugilite", "C", "I", False, None, None),
    (31, "amethyst", "V", "I", False, "nekorogear:amethyst", "amethyst"),
    (32, "rhodochrosite", "C", "I", False, None, None),
    (33, "kunzite", "C", "I", False, None, None),
    (34, "aquamarine", "C", "D", False, None, None),
    (35, "silver", "M", "I", True, None, None),
    (36, "iron", "V", None, True, None, None),
    (37, "tin", "M", "S", True, None, None),
    (38, "lead", "M", "S", True, None, None),
    (39, "onyx", "C", "D", False, None, None),
    (40, "netherite", "V", None, True, None, None),
]

TOOLS = ["sword", "shovel", "pickaxe", "axe", "hoe"]
ARMOR = ["helmet", "chestplate", "leggings", "boots"]
LEVEL_JAVA = {"W": "Level.WEAK", "S": "Level.STONE", "I": "Level.IRON", "D": "Level.DIAMOND", None: "null"}
# ore veins per level: vein size, veins per chunk, lowest and highest y (trapezoid, most in the middle)
# Ores spread exactly like the vanilla ore of the same strength (copper for stone level, iron, diamond):
# level -> vanilla ore, [(vanilla configured feature, vanilla placed feature, our suffix)].
ORE = {
    "S": ("copper", [("ore_copper_small", "ore_copper", "")]),
    "I": ("iron", [("ore_iron", "ore_iron_upper", "_upper"), ("ore_iron", "ore_iron_middle", "_middle"),
                   ("ore_iron_small", "ore_iron_small", "_small")]),
    "D": ("diamond", [("ore_diamond_small", "ore_diamond", ""), ("ore_diamond_medium", "ore_diamond_medium", "_medium"),
                      ("ore_diamond_large", "ore_diamond_large", "_large"), ("ore_diamond_buried", "ore_diamond_buried", "_buried")]),
}


def ore_features(m):
    """Copies the vanilla configured and placed ore features with this material's ores; returns the placed ids."""
    out = []
    for configured, placed, suffix in ORE[m.level][1]:
        name = f"{m.name}_ore{suffix}"
        conf = json.loads(jar.read(f"data/minecraft/worldgen/configured_feature/{configured}.json").decode())
        for target in conf["config"]["targets"]:
            deep = "deepslate" in target["state"]["Name"]
            target["state"] = {"Name": f"{NS}:deepslate_{m.name}_ore" if deep else f"{NS}:{m.name}_ore"}
        if m.kind == "C":
            # crystals: single blocks, and only every second vein makes one (scattered_ore of size 1 places 0 or 1)
            conf["type"] = "minecraft:scattered_ore"
            conf["config"]["size"] = 1
        write_json(f"data/{NS}/worldgen/configured_feature/{name}.json", conf)
        place = json.loads(jar.read(f"data/minecraft/worldgen/placed_feature/{placed}.json").decode())
        place["feature"] = f"{NS}:{name}"
        # how many veins stay below and above the deepslate layer (options.json); before the biome check, which stays last
        place["placement"].insert(len(place["placement"]) - 1, {"type": f"{NS}:ore_amount"})
        write_json(f"data/{NS}/worldgen/placed_feature/{name}.json", place)
        out.append(f"{NS}:{name}")
    return out

jar = zipfile.ZipFile(JAR)
written = set()


def path_of(*parts):
    p = os.path.join(*parts)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


def write_json(rel, obj):
    p = path_of(RES, rel)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, indent=2)
        f.write("\n")
    written.add(os.path.normpath(p))


def title(name):
    return " ".join(w.capitalize() for w in name.split("_"))


class M:
    def __init__(self, row):
        self.coin, self.name, self.kind, self.level, self.metal, self.vrepair, self.extra = row
        self.label = title(self.name)

    @property
    def tools(self):
        return self.level is not None

    @property
    def repair(self):
        if self.kind == "C":
            return f"{NS}:{self.name}"
        if self.kind in "MA":
            return f"{NS}:{self.name}_ingot"
        return self.vrepair


MATS = [M(r) for r in MATERIALS]


# ---------------------------------------------------------------- textures

def vanilla(rel):
    return Image.open(io.BytesIO(jar.read("assets/minecraft/textures/" + rel + ".png"))).convert("RGBA")


def palette_of(img):
    return {p[:3] for p in img.getdata() if p[3] > 0}


STICK = palette_of(vanilla("item/stick"))
STONE = palette_of(vanilla("block/stone"))
DEEPSLATE = palette_of(vanilla("block/deepslate"))


def lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def coin_ramp(coin):
    """The 6 colours of the coin as drawn, dark to light."""
    img = Image.open(original(coin, "coin")).convert("RGBA")
    return sorted(palette_of(img), key=lum)


def shift(stops, target):
    """Moves a ramp so its main colour (4th of 6) becomes target, keeping the user's shading (hue shifts, steps)."""
    mh, ml, ms = colorsys.rgb_to_hls(*(v / 255 for v in stops[3]))
    th, tl, ts = colorsys.rgb_to_hls(*(int(target[i:i + 2], 16) / 255 for i in (1, 3, 5)))
    grey = ms < 0.2  # nearly grey ramps: hue shifts would only make stray colours
    out = []
    for c in stops:
        h, l, s = colorsys.rgb_to_hls(*(v / 255 for v in c))
        l = l * tl / ml if l <= ml else 1 - (1 - l) * (1 - tl) / (1 - ml)
        if grey:
            h, s = th, ts * 0.8
        else:
            h = (h + th - mh) % 1.0
            s = min(1.0, s * ts / ms)
        out.append(tuple(round(v * 255) for v in colorsys.hls_to_rgb(h, min(1.0, max(0.0, l)), s)))
    return out


def ramp(coin):
    """The colours a material uses: vanilla colours for vanilla materials, a shifted coin ramp for moved colours,
    otherwise the coin's own."""
    if coin in TARGET:
        return shift(coin_ramp(coin), TARGET[coin])
    if coin not in CORRECT:
        return coin_ramp(coin)
    img = vanilla(CORRECT[coin])
    colours = sorted(palette_of(img.crop((0, 0, img.width, img.width))), key=lum)
    n = len(coin_ramp(coin))
    if len(colours) >= n:
        return [colours[round(i * (len(colours) - 1) / (n - 1))] for i in range(n)]
    # too few colours: add darker shades of the darkest one below them
    missing = n - len(colours)
    dark = colours[0]
    factors = [0.35 + 0.45 * i / (missing - 1) for i in range(missing)] if missing > 1 else [0.5]
    shades = [tuple(round(c * f) for c in dark) for f in factors]
    return shades + colours


def corrected_coins():
    """Coins and bags with the corrected colours, for comparing; the Coins and Collector Edition mods stay as they are."""
    out = os.path.join(MOD, "art", "coins and bags corrected")
    os.makedirs(out, exist_ok=True)
    for coin in sorted(set(CORRECT) | set(TARGET)):
        table = dict(zip(coin_ramp(coin), ramp(coin)))
        for kind, src in (("coin", original(coin, "coin")), ("bag", original(coin, "bag"))):
            img = Image.open(src).convert("RGBA")
            px = img.load()
            for y in range(img.height):
                for x in range(img.width):
                    r, g, b, a = px[x, y]
                    if a and (r, g, b) in table:
                        px[x, y] = table[(r, g, b)] + (a,)
            img.save(os.path.join(out, f"{coin:03} {kind}.png"))


def coin_image(coin, corrected):
    p = os.path.join(MOD, "art", "coins and bags corrected", f"{coin:03} coin.png")
    if corrected and os.path.exists(p):
        return Image.open(p).convert("RGBA")
    return Image.open(original(coin, "coin")).convert("RGBA")


def bag_image(coin):
    p = os.path.join(MOD, "art", "coins and bags corrected", f"{coin:03} bag.png")
    return Image.open(p if os.path.exists(p) else original(coin, "bag")).convert("RGBA")


def sample(stops, t):
    t = min(max(t, 0.0), 1.0) * (len(stops) - 1)
    i = min(int(t), len(stops) - 2)
    f = t - i
    a, b = stops[i], stops[i + 1]
    return tuple(round(a[k] + (b[k] - a[k]) * f) for k in range(3))


def recolour(img, stops, keep=frozenset(), low=0.0, high=1.0, mid=None, gain=2.0):
    """Maps the brightness of every pixel (except colours in keep) onto the coin's colour ramp,
    using only the part of the ramp between low and high (0 = darkest colour, 1 = lightest).
    With mid, the texture's own contrast is kept instead: its average brightness lands at mid,
    and differences are only multiplied by gain (for soft textures like smooth quartz)."""
    img = img.copy()
    colours = palette_of(img) - keep
    if not colours:
        return img
    lo = min(lum(c) for c in colours)
    hi = max(lum(c) for c in colours)
    span = hi - lo or 1.0
    if mid is not None:
        px_l = [lum(p[:3]) for p in img.getdata() if p[3] > 0 and p[:3] in colours]
        mean = sum(px_l) / len(px_l)
        table = {c: sample(stops, mid + gain * (lum(c) - mean) / 255) for c in colours}
    else:
        table = {c: sample(stops, low + (high - low) * (lum(c) - lo) / span) for c in colours}
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            if a and (r, g, b) in table:
                px[x, y] = table[(r, g, b)] + (a,)
    return img


def shape_of(name):
    return next((s for s, names in SHAPES.items() if name in names), None)


def from_template(shape, stops):
    """The user's grey template coloured with the material's 6 colours."""
    img = Image.open(os.path.join(MOD, "art", "crystal shapes", "templates", f"{shape}.png")).convert("RGBA")
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, gr, b, a = px[x, y]
            if a:
                i = min(range(6), key=lambda k: sum((c - d) ** 2 for c, d in zip((r, gr, b), SHAPE_GREYS[k])))
                px[x, y] = stops[i] + (a,)
    return img


def save_texture(rel, img):
    if rel in KEEP:
        return
    p = path_of(ASSETS, "textures", rel + ".png")
    img.save(p)
    written.add(os.path.normpath(p))


def textures(m):
    stops = ramp(m.coin)
    look = "iron" if m.metal else "diamond"
    n = m.name
    if m.kind == "C":
        shape = shape_of(n)
        save_texture(f"item/{n}", from_template(shape, stops) if shape else recolour(vanilla("item/diamond"), stops))
        save_texture(f"item/{n}_shard", recolour(vanilla("item/amethyst_shard"), stops))
        save_texture(f"block/{n}_block", recolour(vanilla("block/diamond_block"), stops))
        save_texture(f"block/{n}_ore", recolour(vanilla("block/diamond_ore"), stops, STONE))
        save_texture(f"block/deepslate_{n}_ore", recolour(vanilla("block/deepslate_diamond_ore"), stops, DEEPSLATE))
    elif m.kind == "M":
        save_texture(f"item/raw_{n}", recolour(vanilla("item/raw_iron"), stops))
        save_texture(f"item/{n}_nugget", recolour(vanilla("item/iron_nugget"), stops))
        save_texture(f"item/{n}_ingot", recolour(vanilla("item/iron_ingot"), stops))
        save_texture(f"block/{n}_block", recolour(vanilla("block/iron_block"), stops))
        save_texture(f"block/raw_{n}_block", recolour(vanilla("block/raw_iron_block"), stops))
        save_texture(f"block/{n}_ore", recolour(vanilla("block/iron_ore"), stops, STONE))
        save_texture(f"block/deepslate_{n}_ore", recolour(vanilla("block/deepslate_iron_ore"), stops, DEEPSLATE))
    elif m.kind == "A":
        save_texture(f"item/{n}_nugget", recolour(vanilla("item/iron_nugget"), stops))
        save_texture(f"item/{n}_ingot", recolour(vanilla("item/iron_ingot"), stops))
        save_texture(f"block/{n}_block", recolour(vanilla("block/iron_block"), stops))
    if m.extra == "copper_nugget":
        save_texture("item/copper_nugget", recolour(vanilla("item/iron_nugget"), stops))
    if m.extra == "amethyst":
        save_texture("item/amethyst", recolour(vanilla("item/diamond"), stops))
    if m.tools:
        prefix = "iron" if m.metal else "diamond"
        for t in TOOLS:
            save_texture(f"item/{n}_{t}", recolour(vanilla(f"item/{prefix}_{t}"), stops, STICK))
        for a in ARMOR:
            save_texture(f"item/{n}_{a}", recolour(vanilla(f"item/{prefix}_{a}"), stops))
        for layer in (1, 2):
            save_texture(f"models/armor/{n}_layer_{layer}", recolour(vanilla(f"models/armor/{look}_layer_{layer}"), stops))


# ---------------------------------------------------------------- decorative blocks

# Item that crafts the decorative blocks of a material without tools here.
DECOR_ITEM = {"gold": "minecraft:gold_ingot", "diamond": "minecraft:diamond", "iron": "minecraft:iron_ingot",
              "netherite": "minecraft:netherite_ingot"}
# (id prefix of stairs/slab, id of the full block, vanilla block it copies)
def decor_sets(n):
    return [(f"large_{n}_brick", f"large_{n}_bricks", "stone_bricks"),
            (f"small_{n}_brick", f"small_{n}_bricks", "nether_bricks"),
            (f"smooth_{n}", f"smooth_{n}", "smooth_quartz")]


def decor_blocks(n):
    out = []
    for prefix, full, _ in decor_sets(n):
        out += [full, f"{prefix}_stairs", f"{prefix}_slab"]
    return out + [f"{n}_pillar", f"{n}_lamp", f"{n}_redstone_lamp"]


def decor_textures(m, stops):
    n = m.name
    save_texture(f"block/large_{n}_bricks", recolour(vanilla("block/stone_bricks"), stops, low=0.1, high=0.9))
    save_texture(f"block/small_{n}_bricks", recolour(vanilla("block/nether_bricks"), stops, low=0.05, high=0.75))
    save_texture(f"block/smooth_{n}", recolour(vanilla("block/quartz_block_bottom"), stops, mid=0.62, gain=2.0))
    save_texture(f"block/{n}_pillar", recolour(vanilla("block/quartz_pillar"), stops, mid=0.6, gain=1.6))
    save_texture(f"block/{n}_pillar_top", recolour(vanilla("block/quartz_pillar_top"), stops, mid=0.6, gain=1.6))
    save_texture(f"block/{n}_lamp", recolour(vanilla("block/sea_lantern"), stops, low=0.35, high=1.0))
    meta = path_of(ASSETS, "textures", "block", f"{n}_lamp.png.mcmeta")
    with open(meta, "wb") as f:
        f.write(jar.read("assets/minecraft/textures/block/sea_lantern.png.mcmeta"))
    written.add(os.path.normpath(meta))
    save_texture(f"block/{n}_redstone_lamp", recolour(vanilla("block/redstone_lamp"), stops, low=0.0, high=0.55))
    save_texture(f"block/{n}_redstone_lamp_on", recolour(vanilla("block/redstone_lamp_on"), stops, low=0.25, high=1.0))


def vanilla_json(rel):
    return jar.read(f"assets/minecraft/{rel}.json").decode("utf-8")


def copy_json(src_rel, dst_rel, replace):
    """A vanilla blockstate or model with its names swapped (longest first, so prefixes do not clash)."""
    text = vanilla_json(src_rel)
    for old in sorted(replace, key=len, reverse=True):
        text = text.replace(old, replace[old])
    write_json(f"assets/{NS}/{dst_rel}.json", json.loads(text))


def decor_assets(m, lang):
    n = m.name
    T = f"{NS}:block/"
    for prefix, full, like in decor_sets(n):
        tex = {"stone_bricks": "minecraft:block/stone_bricks", "nether_bricks": "minecraft:block/nether_bricks",
               "smooth_quartz": "minecraft:block/quartz_block_bottom"}[like]
        vprefix = {"stone_bricks": "stone_brick", "nether_bricks": "nether_brick", "smooth_quartz": "smooth_quartz"}[like]
        write_json(f"assets/{NS}/models/block/{full}.json", {"parent": "minecraft:block/cube_all", "textures": {"all": T + full}})
        write_json(f"assets/{NS}/blockstates/{full}.json", {"variants": {"": {"model": T + full}}})
        for suffix in ("_stairs", "_stairs_inner", "_stairs_outer", "_slab", "_slab_top"):
            copy_json(f"models/block/{vprefix}{suffix}", f"models/block/{prefix}{suffix}", {tex: T + full})
        copy_json(f"blockstates/{vprefix}_stairs", f"blockstates/{prefix}_stairs",
                  {f"minecraft:block/{vprefix}_stairs": f"{T}{prefix}_stairs"})
        copy_json(f"blockstates/{vprefix}_slab", f"blockstates/{prefix}_slab",
                  {f"minecraft:block/{vprefix}_slab": f"{T}{prefix}_slab", f"minecraft:block/{like}": T + full})
        for b in (full, f"{prefix}_stairs", f"{prefix}_slab"):
            write_json(f"assets/{NS}/models/item/{b}.json", {"parent": T + b})
    copy_json("models/block/quartz_pillar", f"models/block/{n}_pillar",
              {"minecraft:block/quartz_pillar_top": f"{T}{n}_pillar_top", "minecraft:block/quartz_pillar": f"{T}{n}_pillar"})
    copy_json("models/block/quartz_pillar_horizontal", f"models/block/{n}_pillar_horizontal",
              {"minecraft:block/quartz_pillar_top": f"{T}{n}_pillar_top", "minecraft:block/quartz_pillar": f"{T}{n}_pillar"})
    copy_json("blockstates/quartz_pillar", f"blockstates/{n}_pillar", {"minecraft:block/quartz_pillar": f"{T}{n}_pillar"})
    write_json(f"assets/{NS}/models/block/{n}_lamp.json", {"parent": "minecraft:block/cube_all", "textures": {"all": f"{T}{n}_lamp"}})
    write_json(f"assets/{NS}/blockstates/{n}_lamp.json", {"variants": {"": {"model": f"{T}{n}_lamp"}}})
    for b in ("redstone_lamp", "redstone_lamp_on"):
        write_json(f"assets/{NS}/models/block/{n}_{b}.json", {"parent": "minecraft:block/cube_all", "textures": {"all": f"{T}{n}_{b}"}})
    copy_json("blockstates/redstone_lamp", f"blockstates/{n}_redstone_lamp", {"minecraft:block/redstone_lamp": f"{T}{n}_redstone_lamp"})
    for b in (f"{n}_pillar", f"{n}_lamp", f"{n}_redstone_lamp"):
        write_json(f"assets/{NS}/models/item/{b}.json", {"parent": T + b})
    for b in decor_blocks(n):
        lang[f"block.{NS}.{b}"] = title(b)


def decor_data(m):
    n = m.name
    # crystals use their shards (only the storage block takes whole crystals); others their ingot or vanilla item
    if m.kind == "C":
        material = f"{NS}:{n}_shard"
    elif n == "amethyst":
        material = "minecraft:amethyst_shard"
    else:
        material = DECOR_ITEM.get(n, m.repair)
    for prefix, full, like in decor_sets(n):
        stairs, slab = f"{NS}:{prefix}_stairs", f"{NS}:{prefix}_slab"
        shaped(f"{prefix}_stairs", ["#  ", "## ", "###"], {"#": f"{NS}:{full}"}, stairs, 4, "building")
        shaped(f"{prefix}_slab", ["###"], {"#": f"{NS}:{full}"}, slab, 6, "building")
        stonecut(f"{NS}:{full}", stairs, 1)
        stonecut(f"{NS}:{full}", slab, 2)
        loot_self(full)
        loot_self(f"{prefix}_stairs")
        loot_slab(f"{prefix}_slab")
        for kind in ("item", "block"):
            tag(kind, "minecraft:stairs", stairs)
            tag(kind, "minecraft:slabs", slab)
        for b in (full, f"{prefix}_stairs", f"{prefix}_slab"):
            tag("block", "minecraft:mineable/pickaxe", f"{NS}:{b}")
    large, small, smooth = f"{NS}:large_{n}_bricks", f"{NS}:small_{n}_bricks", f"{NS}:smooth_{n}"
    shaped(f"large_{n}_bricks", ["###", "#X#", "###"], {"#": "minecraft:stone_bricks", "X": material}, large, 8, "building")
    shaped(f"small_{n}_bricks", ["##", "##"], {"#": large}, small, 4, "building")
    stonecut(large, small, 1)
    stonecut(large, f"{NS}:small_{n}_brick_stairs", 1)
    stonecut(large, f"{NS}:small_{n}_brick_slab", 2)
    shaped(f"smooth_{n}", ["###", "#X#", "###"], {"#": "minecraft:smooth_stone", "X": material}, smooth, 8, "building")
    shaped(f"{n}_pillar", ["#", "#"], {"#": smooth}, f"{NS}:{n}_pillar", 2, "building")
    stonecut(smooth, f"{NS}:{n}_pillar", 1)
    shaped(f"{n}_lamp", ["DGD", "GXG", "DGD"], {"D": "minecraft:glowstone_dust", "G": "minecraft:glass", "X": material},
           f"{NS}:{n}_lamp", 2, "building")
    write_json(f"data/{NS}/recipe/{n}_redstone_lamp.json", {
        "type": "minecraft:crafting_shapeless", "category": "redstone",
        "ingredients": [ing("minecraft:redstone_lamp"), ing(material)], "result": {"count": 1, "id": f"{NS}:{n}_redstone_lamp"}})
    for b in (f"{n}_pillar", f"{n}_lamp", f"{n}_redstone_lamp"):
        loot_self(b)
    tag("block", "minecraft:mineable/pickaxe", f"{NS}:{n}_pillar")


def stonecut(src, result, count):
    name = result.split(":")[1] + "_from_" + src.split(":")[1] + "_stonecutting"
    write_json(f"data/{NS}/recipe/{name}.json", {
        "type": "minecraft:stonecutting", "ingredient": ing(src), "result": {"count": count, "id": result}})


def loot_slab(block):
    write_json(f"data/{NS}/loot_table/blocks/{block}.json", {
        "type": "minecraft:block",
        "pools": [{"bonus_rolls": 0.0, "entries": [{"type": "minecraft:item", "name": f"{NS}:{block}", "functions": [
            {"add": False, "count": 2.0, "function": "minecraft:set_count", "conditions": [{
                "block": f"{NS}:{block}", "condition": "minecraft:block_state_property",
                "properties": {"type": "double"}}]},
            {"function": "minecraft:explosion_decay"}]}], "rolls": 1.0}],
        "random_sequence": f"{NS}:blocks/{block}"})


# ---------------------------------------------------------------- names of things

def material_items(m):
    """(id, kind) of every item that is not a tool: kind is 'item' or 'block'."""
    n = m.name
    if m.kind == "C":
        return [(n, "item"), (f"{n}_shard", "item"), (f"{n}_block", "block"), (f"{n}_ore", "block"), (f"deepslate_{n}_ore", "block")]
    if m.kind == "M":
        return [(f"raw_{n}", "item"), (f"{n}_nugget", "item"), (f"{n}_ingot", "item"), (f"{n}_block", "block"),
                (f"raw_{n}_block", "block"), (f"{n}_ore", "block"), (f"deepslate_{n}_ore", "block")]
    if m.kind == "A":
        return [(f"{n}_nugget", "item"), (f"{n}_ingot", "item"), (f"{n}_block", "block")]
    return [(m.extra, "item")] if m.extra else []


def gear_items(m):
    return [f"{m.name}_{t}" for t in TOOLS + ARMOR] if m.tools else []


def lang_name(m, item_id):
    n, L = m.name, m.label
    names = {
        n: L, f"{n}_shard": f"{L} Shard", f"{n}_block": f"Block of {L}", f"{n}_ore": f"{L} Ore",
        f"deepslate_{n}_ore": f"Deepslate {L} Ore", f"raw_{n}": f"Raw {L}", f"{n}_nugget": f"{L} Nugget",
        f"{n}_ingot": f"{L} Ingot", f"raw_{n}_block": f"Block of Raw {L}",
    }
    return names.get(item_id, title(item_id))


# ---------------------------------------------------------------- assets

def assets():
    lang = {"itemGroup.nekoro": "Nekoro", f"item.{NS}.nekoro_icon": "Amethyst Cat Coin"}
    write_json(f"assets/{NS}/models/item/nekoro_icon.json",
               {"parent": "minecraft:item/generated", "textures": {"layer0": f"{NS}:item/nekoro_icon"}})
    for m in MATS:
        for item_id, kind in material_items(m):
            if kind == "block":
                lang[f"block.{NS}.{item_id}"] = lang_name(m, item_id)
                write_json(f"assets/{NS}/blockstates/{item_id}.json", {"variants": {"": {"model": f"{NS}:block/{item_id}"}}})
                write_json(f"assets/{NS}/models/block/{item_id}.json",
                           {"parent": "minecraft:block/cube_all", "textures": {"all": f"{NS}:block/{item_id}"}})
                write_json(f"assets/{NS}/models/item/{item_id}.json", {"parent": f"{NS}:block/{item_id}"})
            else:
                lang[f"item.{NS}.{item_id}"] = lang_name(m, item_id)
                write_json(f"assets/{NS}/models/item/{item_id}.json",
                           {"parent": "minecraft:item/generated", "textures": {"layer0": f"{NS}:item/{item_id}"}})
        for item_id in gear_items(m):
            lang[f"item.{NS}.{item_id}"] = lang_name(m, item_id)
            parent = "minecraft:item/handheld" if item_id.rsplit("_", 1)[1] in TOOLS else "minecraft:item/generated"
            write_json(f"assets/{NS}/models/item/{item_id}.json", {"parent": parent, "textures": {"layer0": f"{NS}:item/{item_id}"}})
        textures(m)
        decor_assets(m, lang)
        decor_textures(m, ramp(m.coin))
    write_json(f"assets/{NS}/lang/en_us.json", lang)
    p = path_of(ASSETS, "textures", "item", "nekoro_icon.png")
    shutil.copyfile(ICON, p)
    written.add(os.path.normpath(p))


# ---------------------------------------------------------------- data

def ing(item):
    return {"item": item}


def shaped(name, pattern, key, result, count=1, category="misc"):
    write_json(f"data/{NS}/recipe/{name}.json", {
        "type": "minecraft:crafting_shaped", "category": category,
        "key": {k: ing(v) for k, v in key.items()}, "pattern": pattern,
        "result": {"count": count, "id": result}})


def shapeless(name, item, result, count):
    write_json(f"data/{NS}/recipe/{name}.json", {
        "type": "minecraft:crafting_shapeless", "category": "misc",
        "ingredients": [ing(item)], "result": {"count": count, "id": result}})


def cooking(name, ingredients, result, xp):
    for kind, time in (("smelting", 200), ("blasting", 100)):
        write_json(f"data/{NS}/recipe/{name}_from_{kind}.json", {
            "type": f"minecraft:{kind}", "category": "misc", "cookingtime": time, "experience": xp,
            "ingredient": [ing(i) for i in ingredients], "result": {"id": result}})


def pack_recipes(small, big, name_up, name_down):
    shaped(name_up, ["###", "###", "###"], {"#": small}, big)
    shapeless(name_down, big, small, 9)


GEAR_PATTERNS = {
    "sword": ["X", "X", "#"], "shovel": ["X", "#", "#"], "pickaxe": ["XXX", " # ", " # "],
    "axe": ["XX", "X#", " #"], "hoe": ["XX", " #", " #"],
    "helmet": ["XXX", "X X"], "chestplate": ["X X", "XXX", "XXX"], "leggings": ["XXX", "X X", "X X"], "boots": ["X X", "X X"],
}


def loot_self(block):
    write_json(f"data/{NS}/loot_table/blocks/{block}.json", {
        "type": "minecraft:block",
        "pools": [{"bonus_rolls": 0.0, "conditions": [{"condition": "minecraft:survives_explosion"}],
                   "entries": [{"type": "minecraft:item", "name": f"{NS}:{block}"}], "rolls": 1.0}],
        "random_sequence": f"{NS}:blocks/{block}"})


def loot_ore(block, drop):
    silk = {"condition": "minecraft:match_tool", "predicate": {"predicates": {"minecraft:enchantments": [
        {"enchantments": "minecraft:silk_touch", "levels": {"min": 1}}]}}}
    write_json(f"data/{NS}/loot_table/blocks/{block}.json", {
        "type": "minecraft:block",
        "pools": [{"bonus_rolls": 0.0, "entries": [{"type": "minecraft:alternatives", "children": [
            {"type": "minecraft:item", "conditions": [silk], "name": f"{NS}:{block}"},
            {"type": "minecraft:item", "functions": [
                {"enchantment": "minecraft:fortune", "formula": "minecraft:ore_drops", "function": "minecraft:apply_bonus"},
                {"function": "minecraft:explosion_decay"}], "name": drop}]}], "rolls": 1.0}],
        "random_sequence": f"{NS}:blocks/{block}"})


tags = {}


def tag(kind, name, value):
    tags.setdefault((kind, name), []).append(value)


def data():
    ores = []
    for m in MATS:
        n = m.name
        if m.kind == "C":
            pack_recipes(f"{NS}:{n}_shard", f"{NS}:{n}", f"{n}_from_shards", f"{n}_shard")
            pack_recipes(f"{NS}:{n}", f"{NS}:{n}_block", f"{n}_block", f"{n}_from_block")
            cooking(n, [f"{NS}:{n}_ore", f"{NS}:deepslate_{n}_ore"], f"{NS}:{n}", 1.0 if m.level == "D" else 0.7)
            loot_self(f"{n}_block")
            for ore in (f"{n}_ore", f"deepslate_{n}_ore"):
                loot_ore(ore, f"{NS}:{n}_shard")  # crystal ores give shards; 9 shards make a crystal
            tag("item", f"c:gems/{n}", f"{NS}:{n}")
            tag("item", "c:gems", f"#c:gems/{n}")
            tag("item", "minecraft:beacon_payment_items", f"{NS}:{n}")
        if m.kind == "M":
            pack_recipes(f"{NS}:{n}_nugget", f"{NS}:{n}_ingot", f"{n}_ingot_from_nuggets", f"{n}_nugget")
            pack_recipes(f"{NS}:{n}_ingot", f"{NS}:{n}_block", f"{n}_block", f"{n}_ingot_from_block")
            pack_recipes(f"{NS}:raw_{n}", f"{NS}:raw_{n}_block", f"raw_{n}_block", f"raw_{n}")
            cooking(f"{n}_ingot", [f"{NS}:raw_{n}", f"{NS}:{n}_ore", f"{NS}:deepslate_{n}_ore"], f"{NS}:{n}_ingot",
                    1.0 if m.level == "D" else 0.7)
            for b in (f"{n}_block", f"raw_{n}_block"):
                loot_self(b)
            for ore in (f"{n}_ore", f"deepslate_{n}_ore"):
                loot_ore(ore, f"{NS}:raw_{n}")
            for t, v in (("ingots", f"{n}_ingot"), ("nuggets", f"{n}_nugget"), ("raw_materials", f"raw_{n}")):
                tag("item", f"c:{t}/{n}", f"{NS}:{v}")
                tag("item", f"c:{t}", f"#c:{t}/{n}")
            tag("item", "minecraft:beacon_payment_items", f"{NS}:{n}_ingot")
            for kind in ("item", "block"):
                tag(kind, f"c:storage_blocks/raw_{n}", f"{NS}:raw_{n}_block")
                tag(kind, "c:storage_blocks", f"#c:storage_blocks/raw_{n}")
            tag("block", "minecraft:mineable/pickaxe", f"{NS}:raw_{n}_block")
            tag("block", "minecraft:needs_stone_tool", f"{NS}:raw_{n}_block")
        if m.kind == "A":
            pack_recipes(f"{NS}:{n}_nugget", f"{NS}:{n}_ingot", f"{n}_ingot_from_nuggets", f"{n}_nugget")
            pack_recipes(f"{NS}:{n}_ingot", f"{NS}:{n}_block", f"{n}_block", f"{n}_ingot_from_block")
            write_json(f"data/{NS}/recipe/{n}_ingot_alloy.json", {
                "type": "minecraft:crafting_shapeless", "category": "misc",
                "ingredients": [ing(i) for i in ALLOYS[n]], "result": {"count": len(ALLOYS[n]), "id": f"{NS}:{n}_ingot"}})
            loot_self(f"{n}_block")
            for t, v in (("ingots", f"{n}_ingot"), ("nuggets", f"{n}_nugget")):
                tag("item", f"c:{t}/{n}", f"{NS}:{v}")
                tag("item", f"c:{t}", f"#c:{t}/{n}")
            tag("item", "minecraft:beacon_payment_items", f"{NS}:{n}_ingot")
            tag("block", "minecraft:mineable/pickaxe", f"{NS}:{n}_block")
            tag("block", "minecraft:needs_stone_tool", f"{NS}:{n}_block")
            tag("block", "minecraft:beacon_base_blocks", f"{NS}:{n}_block")
            for kind in ("item", "block"):
                tag(kind, f"c:storage_blocks/{n}", f"{NS}:{n}_block")
                tag(kind, "c:storage_blocks", f"#c:storage_blocks/{n}")
        if m.kind in "CM":
            needs ="minecraft:needs_iron_tool" if m.level == "D" else "minecraft:needs_stone_tool"
            for b in (f"{n}_block", f"{n}_ore", f"deepslate_{n}_ore"):
                tag("block", "minecraft:mineable/pickaxe", f"{NS}:{b}")
                tag("block", needs, f"{NS}:{b}")
            tag("block", "minecraft:beacon_base_blocks", f"{NS}:{n}_block")
            for kind in ("item", "block"):
                tag(kind, f"c:storage_blocks/{n}", f"{NS}:{n}_block")
                tag(kind, "c:storage_blocks", f"#c:storage_blocks/{n}")
                tag(kind, f"c:ores/{n}", f"{NS}:{n}_ore")
                tag(kind, f"c:ores/{n}", f"{NS}:deepslate_{n}_ore")
                tag(kind, "c:ores", f"#c:ores/{n}")
                tag(kind, "c:ores_in_ground/stone", f"{NS}:{n}_ore")
                tag(kind, "c:ores_in_ground/deepslate", f"{NS}:deepslate_{n}_ore")
            ores += ore_features(m)
        if m.extra == "copper_nugget":
            pack_recipes(f"{NS}:copper_nugget", "minecraft:copper_ingot", "copper_ingot_from_nuggets", "copper_nugget")
            tag("item", "c:nuggets/copper", f"{NS}:copper_nugget")
            tag("item", "c:nuggets", "#c:nuggets/copper")
        if m.extra == "amethyst":
            pack_recipes("minecraft:amethyst_shard", f"{NS}:amethyst", "amethyst", "amethyst_shard")
        if m.tools:
            for g in TOOLS + ARMOR:
                key = {"X": m.repair}
                if g in TOOLS:
                    key["#"] = "minecraft:stick"
                shaped(f"{n}_{g}", GEAR_PATTERNS[g], key, f"{NS}:{n}_{g}", category="equipment")
            for t in TOOLS:
                tag("item", f"minecraft:{t}s", f"{NS}:{n}_{t}")
            for a, t in zip(ARMOR, ("head_armor", "chest_armor", "leg_armor", "foot_armor")):
                tag("item", f"minecraft:{t}", f"{NS}:{n}_{a}")
                tag("item", "minecraft:trimmable_armor", f"{NS}:{n}_{a}")
            nugget = f"{NS}:{n}_nugget" if m.kind in "MA" else (f"{NS}:copper_nugget" if n == "copper" else None)
            if nugget:
                cooking(nugget.split(":")[1], [f"{NS}:{n}_{g}" for g in TOOLS + ARMOR], nugget, 0.1)
        decor_data(m)
    write_json(f"data/{NS}/neoforge/biome_modifier/ores.json",
               {"type": f"{NS}:ores", "biomes": "#minecraft:is_overworld", "features": ores})
    for (kind, name), values in tags.items():
        ns, path = name.split(":")
        write_json(f"data/{ns}/tags/{kind}/{path}.json", {"replace": False, "values": list(dict.fromkeys(values))})


# ---------------------------------------------------------------- java

def java():
    lines = []
    for m in MATS:
        kind = {"C": "CRYSTAL", "M": "METAL", "A": "ALLOY", "V": "VANILLA"}[m.kind]
        repair = f'"{m.repair}"' if m.repair else "null"
        extra = f'"{m.extra}"' if m.extra else "null"
        lines.append(f'            new GearMaterial({m.coin}, "{m.name}", GearMaterial.Kind.{kind}, {LEVEL_JAVA[m.level]}, '
                     f'{repair}, {str(m.metal).lower()}, {extra})')
    features = [f'"{m.name}_ore{suffix}"' for m in MATS if m.kind in "CM" for _, _, suffix in ORE[m.level][1]]
    text = ("package dev.xardas.nekorogear;\n\nimport java.util.List;\n\n"
            "/** The 40 materials in coin colour order. Generated by source/tools/generate.py; edit the list there. */\n"
            "public final class GearMaterials {\n    private GearMaterials() { }\n\n"
            "    public static final List<GearMaterial> ALL = List.of(\n" + ",\n".join(lines) + ");\n\n"
            "    /** Placed ore features (spread like the vanilla ore of the same strength). */\n"
            "    public static final List<String> ORE_FEATURES = List.of(\n            "
            + ",\n            ".join(features) + ");\n}\n")
    with open(JAVA, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


# ---------------------------------------------------------------- preview

# Vanilla items shown in the preview: material, piece, raw, block, raw block, ore, deepslate ore ("own:" = this mod's).
VANILLA_ITEMS = {
    "redstone": ["item/redstone", None, None, "block/redstone_block", None, "block/redstone_ore", "block/deepslate_redstone_ore"],
    "copper": ["item/copper_ingot", "own:item/copper_nugget", "item/raw_copper", "block/copper_block", "block/raw_copper_block",
               "block/copper_ore", "block/deepslate_copper_ore"],
    "gold": ["item/gold_ingot", "item/gold_nugget", "item/raw_gold", "block/gold_block", "block/raw_gold_block",
             "block/gold_ore", "block/deepslate_gold_ore"],
    "emerald": ["item/emerald", None, None, "block/emerald_block", None, "block/emerald_ore", "block/deepslate_emerald_ore"],
    "diamond": ["item/diamond", None, None, "block/diamond_block", None, "block/diamond_ore", "block/deepslate_diamond_ore"],
    "lapis": ["item/lapis_lazuli", None, None, "block/lapis_block", None, "block/lapis_ore", "block/deepslate_lapis_ore"],
    "amethyst": ["own:item/amethyst", "item/amethyst_shard", None, "block/amethyst_block", None, "block/budding_amethyst", None],
    "iron": ["item/iron_ingot", "item/iron_nugget", "item/raw_iron", "block/iron_block", "block/raw_iron_block",
             "block/iron_ore", "block/deepslate_iron_ore"],
    "netherite": ["item/netherite_ingot", "item/netherite_scrap", None, "block/netherite_block", None, "block/ancient_debris_side", None],
}


def preview():
    """One row per colour: coin, bag, then every texture of that material."""
    cell, label = 32, 120
    columns = ["before", "coin", "bag", "material", "piece", "raw", "block", "raw block", "ore", "deepslate"] + TOOLS + ARMOR
    img = Image.new("RGBA", (label + cell * len(columns), cell * (len(MATS) + 1)), (40, 40, 48, 255))
    draw = ImageDraw.Draw(img)
    for i, c in enumerate(columns):
        draw.text((label + i * cell + 1, 10), c[:6], fill=(200, 200, 200, 255))

    def put(col, row, im):
        if im is None:
            return
        im = im.crop((0, 0, im.width, im.width)).resize((cell, cell), Image.NEAREST)
        img.alpha_composite(im, (label + col * cell, (row + 1) * cell))

    def own(rel):
        p = os.path.join(ASSETS, "textures", rel + ".png")
        return Image.open(p).convert("RGBA") if os.path.exists(p) else None

    def van(rel):
        try:
            return vanilla(rel)
        except KeyError:
            return None

    for row, m in enumerate(MATS):
        n = m.name
        draw.text((4, (row + 1) * cell + 10), f"{m.coin:2} {m.label}", fill=(230, 230, 230, 255))
        put(0, row, coin_image(m.coin, False))
        put(1, row, coin_image(m.coin, True))
        put(2, row, bag_image(m.coin))
        if m.kind == "C":
            items = [own(f"item/{n}"), own(f"item/{n}_shard"), None, own(f"block/{n}_block"), None,
                     own(f"block/{n}_ore"), own(f"block/deepslate_{n}_ore")]
        elif m.kind == "M":
            items = [own(f"item/{n}_ingot"), own(f"item/{n}_nugget"), own(f"item/raw_{n}"), own(f"block/{n}_block"),
                     own(f"block/raw_{n}_block"), own(f"block/{n}_ore"), own(f"block/deepslate_{n}_ore")]
        elif m.kind == "A":
            items = [own(f"item/{n}_ingot"), own(f"item/{n}_nugget"), None, own(f"block/{n}_block")]
        else:
            items = [van(v) if v and not v.startswith("own:") else (own(v[4:]) if v else None)
                     for v in VANILLA_ITEMS.get(n, [])]
        for i, im in enumerate(items):
            put(3 + i, row, im)
        for i, g in enumerate(TOOLS + ARMOR):
            if m.tools:
                put(10 + i, row, own(f"item/{n}_{g}"))
            else:
                vname = {"gold": "golden"}.get(n, n)
                put(10 + i, row, van(f"item/{vname}_{g}"))
    big = img.resize((img.width * 2, img.height * 2), Image.NEAREST)
    big.save(os.path.join(MOD, "art", "preview.png"))


def preview_blocks():
    """One row per colour: coin, then the decorative block textures."""
    cell, label = 32, 120
    columns = [("coin", None), ("large", "large_{n}_bricks"), ("small", "small_{n}_bricks"), ("smooth", "smooth_{n}"),
               ("pillar", "{n}_pillar"), ("p. top", "{n}_pillar_top"), ("lamp", "{n}_lamp"),
               ("rs off", "{n}_redstone_lamp"), ("rs on", "{n}_redstone_lamp_on")]
    img = Image.new("RGBA", (label + cell * len(columns), cell * (len(MATS) + 1)), (40, 40, 48, 255))
    draw = ImageDraw.Draw(img)
    for i, (head, _) in enumerate(columns):
        draw.text((label + i * cell + 1, 10), head, fill=(200, 200, 200, 255))
    for row, m in enumerate(MATS):
        y = (row + 1) * cell
        draw.text((4, y + 10), f"{m.coin:2} {m.label}", fill=(230, 230, 230, 255))
        for i, (_, pattern) in enumerate(columns):
            if pattern is None:
                im = coin_image(m.coin, True)
            else:
                im = Image.open(os.path.join(ASSETS, "textures", "block", pattern.format(n=m.name) + ".png")).convert("RGBA")
            im = im.crop((0, 0, im.width, im.width)).resize((cell, cell), Image.NEAREST)
            img.alpha_composite(im, (label + i * cell, y))
    img.resize((img.width * 2, img.height * 2), Image.NEAREST).save(os.path.join(MOD, "art", "preview-blocks.png"))


def clean():
    """Removes generated files that are no longer produced (e.g. a renamed material)."""
    for base in (os.path.join(ASSETS), os.path.join(DATA)):
        for dp, dn, fn in os.walk(base):
            for f in fn:
                p = os.path.normpath(os.path.join(dp, f))
                rel = os.path.relpath(p, os.path.join(ASSETS, "textures")).replace(os.sep, "/")[:-4]
                if p not in written and rel not in KEEP:
                    os.remove(p)


if __name__ == "__main__":
    java()
    corrected_coins()
    assets()
    data()
    clean()
    preview()
    preview_blocks()
    print("generated", len(written), "files")
