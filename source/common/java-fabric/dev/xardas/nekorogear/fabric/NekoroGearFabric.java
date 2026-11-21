package dev.xardas.nekorogear.fabric;

import java.util.function.Supplier;

import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.biome.v1.BiomeModifications;
import net.fabricmc.fabric.api.biome.v1.BiomeSelectors;
import net.fabricmc.fabric.api.itemgroup.v1.FabricItemGroup;
import net.fabricmc.fabric.api.itemgroup.v1.ItemGroupEvents;
import net.fabricmc.loader.api.FabricLoader;
import net.minecraft.core.Holder;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.item.ArmorMaterial;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.levelgen.GenerationStep;

import dev.xardas.nekorogear.OreAmount;
import dev.xardas.nekorogear.GearConfig;
import dev.xardas.nekorogear.GearMaterials;
import dev.xardas.nekorogear.NekoroGear;
import dev.xardas.nekorogear.NekoroTab;
import dev.xardas.nekorogear.Registrar;

/** Fabric entry point: registers everything at once and adds the ores to Overworld biomes. */
public final class NekoroGearFabric implements ModInitializer {
    @Override
    public void onInitialize() {
        GearConfig.load(FabricLoader.getInstance().getConfigDir());
        Registry.register(BuiltInRegistries.PLACEMENT_MODIFIER_TYPE, NekoroGear.id(OreAmount.NAME), OreAmount.TYPE);
        NekoroGear.registerAll(new Registrar() {
            @Override
            public Supplier<Block> block(String name, Supplier<Block> factory) {
                Block block = Registry.register(BuiltInRegistries.BLOCK, NekoroGear.id(name), factory.get());
                return () -> block;
            }

            @Override
            public Supplier<Item> item(String name, Supplier<Item> factory) {
                Item item = Registry.register(BuiltInRegistries.ITEM, NekoroGear.id(name), factory.get());
                return () -> item;
            }

            @Override
            public Holder<ArmorMaterial> armorMaterial(String name, Supplier<ArmorMaterial> factory) {
                return Registry.registerForHolder(BuiltInRegistries.ARMOR_MATERIAL, NekoroGear.id(name), factory.get());
            }
        });

        if (!NekoroTab.registered()) {
            Registry.register(BuiltInRegistries.CREATIVE_MODE_TAB, NekoroTab.KEY, FabricItemGroup.builder()
                    .title(Component.translatable(NekoroTab.TITLE)).icon(NekoroTab::icon).build());
        }
        ItemGroupEvents.modifyEntriesEvent(NekoroTab.KEY).register(entries -> NekoroGear.TAB_ITEMS.forEach(item -> entries.accept(item.get())));

        if (GearConfig.oreGeneration()) {
            for (String feature : GearMaterials.ORE_FEATURES) {
                BiomeModifications.addFeature(BiomeSelectors.foundInOverworld(), GenerationStep.Decoration.UNDERGROUND_ORES,
                        ResourceKey.create(Registries.PLACED_FEATURE, NekoroGear.id(feature)));
            }
        }
    }
}
