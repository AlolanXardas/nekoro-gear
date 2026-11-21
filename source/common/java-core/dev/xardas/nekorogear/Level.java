package dev.xardas.nekorogear;

/**
 * Strength group of a material. It decides how its ore spreads (like copper, iron or diamond ore), the XP of its ore
 * and the sound of its armor. The stats of tools and armor are in config/Nekoro/Gear/items.json instead.
 * WEAK is for redstone and lapis.
 */
public enum Level {
    WEAK, STONE, IRON, DIAMOND
}
