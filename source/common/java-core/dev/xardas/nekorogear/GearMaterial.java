package dev.xardas.nekorogear;

/**
 * One of the 40 materials, numbered like the coin colours of Nekoro Coins.
 *
 * @param coin   number of the coin colour (1-40)
 * @param name   id part, e.g. "ruby" gives ruby, ruby_shard, ruby_sword
 * @param kind   what new items the material brings
 * @param level  tool and armour strength; null for vanilla materials that already have tools
 * @param repair item that repairs the tools and armour (and crafts them)
 * @param metal  metal look and sounds (iron-like) instead of crystal (diamond-like)
 * @param extra  one extra item for a vanilla material (copper nugget, full amethyst crystal), or null
 */
public record GearMaterial(int coin, String name, Kind kind, Level level, String repair, boolean metal, String extra) {
    public enum Kind {
        /** New crystal: crystal, shard, block, ores. */
        CRYSTAL,
        /** New metal: raw, nugget, ingot, block, raw block, ores. */
        METAL,
        /** New alloy, crafted from other ingots: nugget, ingot, block; no raw form and no ore. */
        ALLOY,
        /** Already in Minecraft; only tools and armour (and maybe one extra item). */
        VANILLA
    }

    public boolean hasTools() {
        return level != null;
    }

    public boolean hasOre() {
        return kind == Kind.CRYSTAL || kind == Kind.METAL;
    }
}
