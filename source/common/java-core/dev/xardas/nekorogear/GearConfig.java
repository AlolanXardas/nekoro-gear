package dev.xardas.nekorogear;

import java.io.Reader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.google.gson.stream.JsonReader;

import net.minecraft.tags.BlockTags;
import net.minecraft.tags.TagKey;
import net.minecraft.world.level.block.Block;

/**
 * config/Nekoro/Gear/options.json (ores) and items.json (the stats of every tool, weapon and armor piece).
 * Read once at start: items are made with these stats, and ores are added to biomes when the game loads.
 */
public final class GearConfig {
    private GearConfig() { }

    /** Values as the game shows them: attack damage and speed include the player's base (1 and 4). */
    public record Tool(int durability, double miningSpeed, String miningTier, double attackDamage, double attackSpeed,
                       int enchantability) { }

    public record Armor(int durability, int defense, double toughness, double knockbackResistance, int enchantability) { }

    public static final List<String> TOOLS = List.of("sword", "shovel", "pickaxe", "axe", "hoe");
    public static final List<String> ARMOR = List.of("helmet", "chestplate", "leggings", "boots");

    /** Defaults of the new crystals: netherite. */
    private static final Map<String, Tool> NETHERITE_TOOLS = Map.of(
            "sword", new Tool(2031, 9, "netherite", 8, 1.6, 15),
            "shovel", new Tool(2031, 9, "netherite", 6.5, 1, 15),
            "pickaxe", new Tool(2031, 9, "netherite", 6, 1.2, 15),
            "axe", new Tool(2031, 9, "netherite", 10, 1, 15),
            "hoe", new Tool(2031, 9, "netherite", 1, 4, 15));
    private static final Map<String, Armor> NETHERITE_ARMOR = Map.of(
            "helmet", new Armor(407, 3, 3, 0.1, 15),
            "chestplate", new Armor(592, 8, 3, 0.1, 15),
            "leggings", new Armor(555, 6, 3, 0.1, 15),
            "boots", new Armor(481, 3, 3, 0.1, 15));

    /**
     * Defaults of metals, alloys and vanilla materials, by their Level, close to a vanilla tier:
     * tool uses, mining speed, damage bonus, mining tier, tool enchantability, armor durability multiplier,
     * defense (helmet, chestplate, leggings, boots), armor enchantability, toughness, axe and hoe damage and speed modifiers.
     */
    private record LevelStats(int uses, double speed, double bonus, String tier, int toolEnchant, int armorMultiplier,
                              int[] defense, int armorEnchant, double toughness, double axeDamage, double axeSpeed,
                              double hoeDamage, double hoeSpeed) { }

    private static final Map<Level, LevelStats> LEVELS = Map.of(
            Level.WEAK, new LevelStats(80, 10, 0.5, "gold", 22, 7, new int[] {2, 5, 3, 1}, 25, 0, 6, -3.0, 0, -3.0),
            Level.STONE, new LevelStats(190, 5, 1.5, "stone", 12, 12, new int[] {2, 5, 4, 1}, 12, 0, 7, -3.2, -1, -2.0),
            Level.IRON, new LevelStats(300, 6.5, 2, "iron", 14, 15, new int[] {2, 6, 5, 2}, 12, 0, 6, -3.1, -2, -1.0),
            Level.DIAMOND, new LevelStats(1300, 8, 3, "diamond", 12, 30, new int[] {3, 8, 6, 3}, 10, 2, 5, -3.0, -3, 0.0));

    private static Tool toolDefault(GearMaterial m, String kind) {
        if (m.kind() == GearMaterial.Kind.CRYSTAL) return NETHERITE_TOOLS.get(kind);
        LevelStats l = LEVELS.get(m.level());
        // damage and speed as the tooltip shows them: 1 + modifier + tier bonus, 4 + speed modifier
        return switch (kind) {
            case "sword" -> new Tool(l.uses(), l.speed(), l.tier(), 1 + 3 + l.bonus(), 4 - 2.4, l.toolEnchant());
            case "shovel" -> new Tool(l.uses(), l.speed(), l.tier(), 1 + 1.5 + l.bonus(), 4 - 3.0, l.toolEnchant());
            case "pickaxe" -> new Tool(l.uses(), l.speed(), l.tier(), 1 + 1 + l.bonus(), 4 - 2.8, l.toolEnchant());
            case "axe" -> new Tool(l.uses(), l.speed(), l.tier(), 1 + l.axeDamage() + l.bonus(), 4 + l.axeSpeed(), l.toolEnchant());
            default -> new Tool(l.uses(), l.speed(), l.tier(), Math.max(1, 1 + l.hoeDamage() + l.bonus()), 4 + l.hoeSpeed(), l.toolEnchant());
        };
    }

    private static Armor armorDefault(GearMaterial m, String kind) {
        if (m.kind() == GearMaterial.Kind.CRYSTAL) return NETHERITE_ARMOR.get(kind);
        LevelStats l = LEVELS.get(m.level());
        int i = ARMOR.indexOf(kind);
        int[] base = {11, 16, 15, 13}; // vanilla durability per piece, times the multiplier
        return new Armor(base[i] * l.armorMultiplier(), l.defense()[i], l.toughness(), 0, l.armorEnchant());
    }

    private static final String OPTIONS = """
            {
              // How many ores of this mod generate in the Overworld, compared with the vanilla ore they copy.
              // 1: as often, 0.5: half, 2: twice, 0: none.
              // ores_in_deepslate: the deepslate layer (below Y 0); ores_in_stone: the stone layer (Y 0 and up).
              // With 0 for both, the materials can come from Nekoro Random Drop. Takes effect after a restart.
              "ores_in_deepslate": 1.0,
              "ores_in_stone": 0.5
            }
            """;

    private static double oresInDeepslate = 1;
    private static double oresInStone = 0.5;
    private static JsonObject items = new JsonObject();

    /** Whether ores are added to biomes at all. */
    public static boolean oreGeneration() {
        return oresInDeepslate > 0 || oresInStone > 0;
    }

    public static double oresInDeepslate() {
        return oresInDeepslate;
    }

    public static double oresInStone() {
        return oresInStone;
    }

    public static void load(Path configDir) {
        Path dir = configDir.resolve("Nekoro").resolve("Gear");
        JsonObject options = read(dir.resolve("options.json"), OPTIONS);
        oresInDeepslate = options.has("ores_in_deepslate") ? Math.max(0, options.get("ores_in_deepslate").getAsDouble()) : 1;
        oresInStone = options.has("ores_in_stone") ? Math.max(0, options.get("ores_in_stone").getAsDouble()) : 0.5;
        items = read(dir.resolve("items.json"), itemsDefaults());
    }

    public static Tool tool(GearMaterial material, String kind) {
        Tool d = toolDefault(material, kind);
        JsonObject o = entry(material.name() + "_" + kind);
        return new Tool(integer(o, "durability", d.durability()), number(o, "mining_speed", d.miningSpeed()),
                o.has("mining_tier") ? o.get("mining_tier").getAsString().toLowerCase(Locale.ROOT) : d.miningTier(),
                number(o, "attack_damage", d.attackDamage()), number(o, "attack_speed", d.attackSpeed()),
                integer(o, "enchantability", d.enchantability()));
    }

    public static Armor armor(GearMaterial material, String kind) {
        Armor d = armorDefault(material, kind);
        JsonObject o = entry(material.name() + "_" + kind);
        return new Armor(integer(o, "durability", d.durability()), integer(o, "defense", d.defense()),
                number(o, "toughness", d.toughness()), number(o, "knockback_resistance", d.knockbackResistance()),
                integer(o, "enchantability", d.enchantability()));
    }

    /** The blocks a tool of this tier cannot get drops from. */
    public static TagKey<Block> incorrectBlocks(String tier) {
        return switch (tier) {
            case "wood" -> BlockTags.INCORRECT_FOR_WOODEN_TOOL;
            case "gold" -> BlockTags.INCORRECT_FOR_GOLD_TOOL;
            case "stone" -> BlockTags.INCORRECT_FOR_STONE_TOOL;
            case "iron" -> BlockTags.INCORRECT_FOR_IRON_TOOL;
            case "diamond" -> BlockTags.INCORRECT_FOR_DIAMOND_TOOL;
            default -> BlockTags.INCORRECT_FOR_NETHERITE_TOOL;
        };
    }

    private static JsonObject entry(String name) {
        return items.has(name) && items.get(name).isJsonObject() ? items.getAsJsonObject(name) : new JsonObject();
    }

    private static int integer(JsonObject o, String key, int fallback) {
        return o.has(key) ? Math.max(1, o.get(key).getAsInt()) : fallback;
    }

    private static double number(JsonObject o, String key, double fallback) {
        return o.has(key) ? Math.max(0, o.get(key).getAsDouble()) : fallback;
    }

    private static String itemsDefaults() {
        StringBuilder out = new StringBuilder("""
                // Nekoro Gear: stats of every tool, weapon and armor piece. Changes take effect after a restart.
                // The new crystals start at netherite level; metals, alloys and vanilla materials near a vanilla tier.
                // durability:           uses before it breaks
                // mining_speed:         how fast a tool mines (netherite 9, diamond 8, iron 6, stone 4)
                // mining_tier:          which blocks drop their items: "wood", "gold", "stone", "iron", "diamond" or "netherite"
                // attack_damage:        damage as the tooltip shows it
                // attack_speed:         attacks per second as the tooltip shows it
                // enchantability:       how good enchantments from the table are (netherite 15, gold 22-25)
                // defense:              armor points
                // toughness:            armor toughness (netherite 3, diamond 2)
                // knockback_resistance: 0 to 1 (netherite 0.1 per piece)
                {
                """);
        Map<String, String> lines = new LinkedHashMap<>();
        for (GearMaterial m : GearMaterials.ALL) {
            if (!m.hasTools()) continue;
            for (String kind : TOOLS) {
                Tool t = toolDefault(m, kind);
                String mining = kind.equals("sword") ? "" : "\"mining_speed\": " + num(t.miningSpeed())
                        + ", \"mining_tier\": \"" + t.miningTier() + "\", ";
                lines.put(m.name() + "_" + kind, "{ \"durability\": " + t.durability() + ", " + mining
                        + "\"attack_damage\": " + num(t.attackDamage()) + ", \"attack_speed\": " + num(t.attackSpeed())
                        + ", \"enchantability\": " + t.enchantability() + " }");
            }
            for (String kind : ARMOR) {
                Armor a = armorDefault(m, kind);
                lines.put(m.name() + "_" + kind, "{ \"durability\": " + a.durability() + ", \"defense\": " + a.defense()
                        + ", \"toughness\": " + num(a.toughness()) + ", \"knockback_resistance\": " + num(a.knockbackResistance())
                        + ", \"enchantability\": " + a.enchantability() + " }");
            }
        }
        int i = 0;
        for (Map.Entry<String, String> e : lines.entrySet()) {
            out.append("  \"").append(e.getKey()).append("\": ").append(e.getValue()).append(++i < lines.size() ? ",\n" : "\n");
        }
        return out.append("}\n").toString();
    }

    private static String num(double value) {
        return value == Math.rint(value) ? String.valueOf((long) value) : String.valueOf(value);
    }

    private static JsonObject read(Path file, String defaults) {
        try {
            if (Files.notExists(file)) {
                Files.createDirectories(file.getParent());
                Files.writeString(file, defaults, StandardCharsets.UTF_8);
            }
            try (Reader reader = Files.newBufferedReader(file, StandardCharsets.UTF_8)) {
                JsonReader json = new JsonReader(reader);
                json.setLenient(true);
                return JsonParser.parseReader(json).getAsJsonObject();
            }
        } catch (Exception e) {
            NekoroGear.LOGGER.error("Could not read {}, using the defaults", file, e);
            JsonReader json = new JsonReader(new java.io.StringReader(defaults));
            json.setLenient(true);
            return JsonParser.parseReader(json).getAsJsonObject();
        }
    }
}
