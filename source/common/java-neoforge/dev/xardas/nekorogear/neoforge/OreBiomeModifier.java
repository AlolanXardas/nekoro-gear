package dev.xardas.nekorogear.neoforge;

import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;

import net.minecraft.core.Holder;
import net.minecraft.core.HolderSet;
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.levelgen.GenerationStep;
import net.minecraft.world.level.levelgen.placement.PlacedFeature;
import net.neoforged.neoforge.common.world.BiomeModifier;
import net.neoforged.neoforge.common.world.ModifiableBiomeInfo;

import dev.xardas.nekorogear.GearConfig;

/** Adds the ores to the given biomes, unless ore generation is off in the config. */
public record OreBiomeModifier(HolderSet<Biome> biomes, HolderSet<PlacedFeature> features) implements BiomeModifier {
    public static final MapCodec<OreBiomeModifier> CODEC = RecordCodecBuilder.mapCodec(i -> i.group(
            Biome.LIST_CODEC.fieldOf("biomes").forGetter(OreBiomeModifier::biomes),
            PlacedFeature.LIST_CODEC.fieldOf("features").forGetter(OreBiomeModifier::features)
    ).apply(i, OreBiomeModifier::new));

    @Override
    public void modify(Holder<Biome> biome, Phase phase, ModifiableBiomeInfo.BiomeInfo.Builder builder) {
        if (phase != Phase.ADD || !GearConfig.oreGeneration() || !biomes.contains(biome)) return;
        for (Holder<PlacedFeature> feature : features) {
            builder.getGenerationSettings().addFeature(GenerationStep.Decoration.UNDERGROUND_ORES, feature);
        }
    }

    @Override
    public MapCodec<? extends BiomeModifier> codec() {
        return CODEC;
    }
}
