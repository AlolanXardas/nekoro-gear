package dev.xardas.nekorogear.neoforge;

import java.util.function.Supplier;

import com.mojang.serialization.MapCodec;

import net.minecraft.core.Holder;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ArmorMaterial;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.loading.FMLPaths;
import net.neoforged.neoforge.common.world.BiomeModifier;
import net.neoforged.neoforge.event.BuildCreativeModeTabContentsEvent;
import net.neoforged.neoforge.registries.DeferredRegister;
import net.neoforged.neoforge.registries.NeoForgeRegistries;
import net.neoforged.neoforge.registries.RegisterEvent;

import net.minecraft.world.level.levelgen.placement.PlacementModifierType;

import dev.xardas.nekorogear.OreAmount;
import dev.xardas.nekorogear.GearConfig;
import dev.xardas.nekorogear.NekoroGear;
import dev.xardas.nekorogear.NekoroTab;
import dev.xardas.nekorogear.Registrar;

/** NeoForge entry point: registers everything through deferred registers and adds the ores to biomes. */
@Mod(NekoroGear.MOD_ID)
public final class NekoroGearNeoForge {
    private static final DeferredRegister.Blocks BLOCKS = DeferredRegister.createBlocks(NekoroGear.MOD_ID);
    private static final DeferredRegister.Items ITEMS = DeferredRegister.createItems(NekoroGear.MOD_ID);
    private static final DeferredRegister<ArmorMaterial> ARMOR = DeferredRegister.create(Registries.ARMOR_MATERIAL, NekoroGear.MOD_ID);
    private static final DeferredRegister<PlacementModifierType<?>> PLACEMENTS =
            DeferredRegister.create(Registries.PLACEMENT_MODIFIER_TYPE, NekoroGear.MOD_ID);
    private static final DeferredRegister<MapCodec<? extends BiomeModifier>> BIOME_MODIFIERS =
            DeferredRegister.create(NeoForgeRegistries.Keys.BIOME_MODIFIER_SERIALIZERS, NekoroGear.MOD_ID);

    public NekoroGearNeoForge(IEventBus modBus) {
        GearConfig.load(FMLPaths.CONFIGDIR.get());        NekoroGear.registerAll(new Registrar() {
            @Override
            public Supplier<Block> block(String name, Supplier<Block> factory) {
                return BLOCKS.register(name, factory);
            }

            @Override
            public Supplier<Item> item(String name, Supplier<Item> factory) {
                return ITEMS.register(name, factory);
            }

            @Override
            public Holder<ArmorMaterial> armorMaterial(String name, Supplier<ArmorMaterial> factory) {
                return ARMOR.register(name, factory);
            }
        });
        BIOME_MODIFIERS.register("ores", () -> OreBiomeModifier.CODEC);
        PLACEMENTS.register(OreAmount.NAME, () -> OreAmount.TYPE);
        PLACEMENTS.register(modBus);
        BLOCKS.register(modBus);
        ITEMS.register(modBus);
        ARMOR.register(modBus);
        BIOME_MODIFIERS.register(modBus);

        modBus.addListener((RegisterEvent event) -> event.register(Registries.CREATIVE_MODE_TAB, helper -> {
            if (!NekoroTab.registered()) {
                helper.register(NekoroTab.KEY, CreativeModeTab.builder().title(Component.translatable(NekoroTab.TITLE)).icon(NekoroTab::icon).build());
            }
        }));
        modBus.addListener((BuildCreativeModeTabContentsEvent event) -> {
            if (event.getTabKey() == NekoroTab.KEY) NekoroGear.TAB_ITEMS.forEach(item -> event.accept(item.get()));
        });
    }
}
