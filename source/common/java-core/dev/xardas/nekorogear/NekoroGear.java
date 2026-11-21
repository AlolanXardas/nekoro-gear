package dev.xardas.nekorogear;

import java.util.ArrayList;
import java.util.EnumMap;
import java.util.List;
import java.util.function.Supplier;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import net.minecraft.core.Holder;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.util.valueproviders.ConstantInt;
import net.minecraft.util.valueproviders.IntProvider;
import net.minecraft.util.valueproviders.UniformInt;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ArmorMaterial;
import net.minecraft.world.item.AxeItem;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.DiggerItem;
import net.minecraft.world.item.HoeItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.PickaxeItem;
import net.minecraft.world.item.ShovelItem;
import net.minecraft.world.item.SwordItem;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.DropExperienceBlock;
import net.minecraft.world.level.block.RedstoneLampBlock;
import net.minecraft.world.level.block.RotatedPillarBlock;
import net.minecraft.world.level.block.SlabBlock;
import net.minecraft.world.level.block.StairBlock;
import net.minecraft.world.level.block.state.BlockBehaviour;

/** Shared constants and registration; each loader passes its own Registrar. */
public final class NekoroGear {
    public static final String MOD_ID = "nekorogear";
    public static final Logger LOGGER = LoggerFactory.getLogger("Nekoro Gear");

    /** Every item of the mod in creative tab order. */
    public static final List<Supplier<Item>> TAB_ITEMS = new ArrayList<>();

    private NekoroGear() { }

    public static ResourceLocation id(String path) {
        return ResourceLocation.fromNamespaceAndPath(MOD_ID, path);
    }

    public static void registerAll(Registrar r) {
        NekoroTab.ICON = r.item(NekoroTab.ICON_NAME, () -> new Item(new Item.Properties()));
        for (GearMaterial m : GearMaterials.ALL) {
            String n = m.name();
            switch (m.kind()) {
                case CRYSTAL -> {
                    item(r, n, () -> new Item(new Item.Properties()));
                    item(r, n + "_shard", () -> new Item(new Item.Properties()));
                    block(r, n + "_block", () -> new Block(BlockBehaviour.Properties.ofFullCopy(Blocks.DIAMOND_BLOCK)));
                    IntProvider xp = m.level() == Level.DIAMOND ? UniformInt.of(3, 7) : UniformInt.of(2, 5);
                    block(r, n + "_ore", () -> new DropExperienceBlock(xp, BlockBehaviour.Properties.ofFullCopy(Blocks.DIAMOND_ORE)));
                    block(r, "deepslate_" + n + "_ore",
                            () -> new DropExperienceBlock(xp, BlockBehaviour.Properties.ofFullCopy(Blocks.DEEPSLATE_DIAMOND_ORE)));
                }
                case METAL -> {
                    item(r, "raw_" + n, () -> new Item(new Item.Properties()));
                    item(r, n + "_nugget", () -> new Item(new Item.Properties()));
                    item(r, n + "_ingot", () -> new Item(new Item.Properties()));
                    block(r, n + "_block", () -> new Block(BlockBehaviour.Properties.ofFullCopy(Blocks.IRON_BLOCK)));
                    block(r, "raw_" + n + "_block", () -> new Block(BlockBehaviour.Properties.ofFullCopy(Blocks.RAW_IRON_BLOCK)));
                    block(r, n + "_ore", () -> new DropExperienceBlock(ConstantInt.of(0), BlockBehaviour.Properties.ofFullCopy(Blocks.IRON_ORE)));
                    block(r, "deepslate_" + n + "_ore",
                            () -> new DropExperienceBlock(ConstantInt.of(0), BlockBehaviour.Properties.ofFullCopy(Blocks.DEEPSLATE_IRON_ORE)));
                }
                case ALLOY -> {
                    item(r, n + "_nugget", () -> new Item(new Item.Properties()));
                    item(r, n + "_ingot", () -> new Item(new Item.Properties()));
                    block(r, n + "_block", () -> new Block(BlockBehaviour.Properties.ofFullCopy(Blocks.IRON_BLOCK)));
                }
                case VANILLA -> {
                    if (m.extra() != null) item(r, m.extra(), () -> new Item(new Item.Properties()));
                }
            }
            if (m.hasTools()) gear(r, m);
            decor(r, m);
        }
    }

    /**
     * Decorative blocks for every material. Ids have two words before "bricks" so Stone Zone (Every Compat) does not
     * take them for new stone types. No recipe turns them back into the material.
     */
    private static void decor(Registrar r, GearMaterial m) {
        String n = m.name();
        for (String[] set : new String[][] {{"large_" + n + "_brick", "large_" + n + "_bricks", "stone_bricks"},
                {"small_" + n + "_brick", "small_" + n + "_bricks", "nether_bricks"},
                {"smooth_" + n, "smooth_" + n, "smooth_quartz"}}) {
            Block like = BuiltInRegistries.BLOCK.get(ResourceLocation.withDefaultNamespace(set[2]));
            Supplier<Block> base = block(r, set[1], () -> new Block(BlockBehaviour.Properties.ofFullCopy(like)));
            block(r, set[0] + "_stairs", () -> new StairBlock(base.get().defaultBlockState(), BlockBehaviour.Properties.ofFullCopy(like)));
            block(r, set[0] + "_slab", () -> new SlabBlock(BlockBehaviour.Properties.ofFullCopy(like)));
        }
        block(r, n + "_pillar", () -> new RotatedPillarBlock(BlockBehaviour.Properties.ofFullCopy(Blocks.QUARTZ_PILLAR)));
        block(r, n + "_lamp", () -> new Block(BlockBehaviour.Properties.ofFullCopy(Blocks.SEA_LANTERN)));
        block(r, n + "_redstone_lamp", () -> new RedstoneLampBlock(BlockBehaviour.Properties.ofFullCopy(Blocks.REDSTONE_LAMP)));
    }

    /** Tools and armor; every item gets its own stats from config/Nekoro/Gear/items.json. */
    private static void gear(Registrar r, GearMaterial m) {
        String n = m.name();
        Supplier<Ingredient> repair = () -> Ingredient.of(BuiltInRegistries.ITEM.get(ResourceLocation.parse(m.repair())));
        for (String kind : GearConfig.TOOLS) {
            GearConfig.Tool s = GearConfig.tool(m, kind);
            GearTier tier = new GearTier(s.durability(), (float) s.miningSpeed(), GearConfig.incorrectBlocks(s.miningTier()),
                    s.enchantability(), repair);
            // the attribute values are added to the player's base attack damage (1) and speed (4)
            Item.Properties props = new Item.Properties()
                    .attributes(DiggerItem.createAttributes(tier, (float) s.attackDamage() - 1, (float) s.attackSpeed() - 4));
            item(r, n + "_" + kind, () -> switch (kind) {
                case "sword" -> new SwordItem(tier, props);
                case "shovel" -> new ShovelItem(tier, props);
                case "pickaxe" -> new PickaxeItem(tier, props);
                case "axe" -> new AxeItem(tier, props);
                default -> new HoeItem(tier, props);
            });
        }

        Holder<SoundEvent> sound = m.level() == Level.WEAK ? SoundEvents.ARMOR_EQUIP_GOLD
                : m.metal() ? SoundEvents.ARMOR_EQUIP_IRON : SoundEvents.ARMOR_EQUIP_DIAMOND;
        ArmorItem.Type[] types = {ArmorItem.Type.HELMET, ArmorItem.Type.CHESTPLATE, ArmorItem.Type.LEGGINGS, ArmorItem.Type.BOOTS};
        for (int i = 0; i < types.length; i++) {
            ArmorItem.Type type = types[i];
            String name = n + "_" + GearConfig.ARMOR.get(i);
            GearConfig.Armor s = GearConfig.armor(m, GearConfig.ARMOR.get(i));
            // one armor material per piece, so toughness and knockback resistance can differ; all use the material's texture
            Holder<ArmorMaterial> material = r.armorMaterial(name, () -> {
                EnumMap<ArmorItem.Type, Integer> defense = new EnumMap<>(ArmorItem.Type.class);
                defense.put(type, s.defense());
                return new ArmorMaterial(defense, s.enchantability(), sound, repair,
                        List.of(new ArmorMaterial.Layer(id(n))), (float) s.toughness(), (float) s.knockbackResistance());
            });
            item(r, name, () -> new ArmorItem(material, type, new Item.Properties().durability(s.durability())));
        }
    }

    private static void item(Registrar r, String name, Supplier<Item> factory) {
        TAB_ITEMS.add(r.item(name, factory));
    }

    private static Supplier<Block> block(Registrar r, String name, Supplier<Block> factory) {
        Supplier<Block> block = r.block(name, factory);
        TAB_ITEMS.add(r.item(name, () -> new BlockItem(block.get(), new Item.Properties())));
        return block;
    }
}
