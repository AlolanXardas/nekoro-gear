package dev.xardas.nekorogear;

import java.util.stream.Stream;

import com.mojang.serialization.MapCodec;

import net.minecraft.core.BlockPos;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.levelgen.placement.PlacementContext;
import net.minecraft.world.level.levelgen.placement.PlacementModifier;
import net.minecraft.world.level.levelgen.placement.PlacementModifierType;

/**
 * Ore placement step "nekorogear:ore_amount": multiplies the veins below Y 0 (the deepslate layer) and from Y 0 up by
 * "ores_in_deepslate" and "ores_in_stone" from options.json. 0 removes them, 0.5 keeps every second one,
 * 2 doubles them (the extra veins go to other places in the same chunk, at the same height).
 */
public final class OreAmount extends PlacementModifier {
    public static final OreAmount INSTANCE = new OreAmount();
    public static final MapCodec<OreAmount> CODEC = MapCodec.unit(() -> INSTANCE);
    public static final String NAME = "ore_amount";
    public static final PlacementModifierType<OreAmount> TYPE = () -> CODEC;

    private OreAmount() { }

    @Override
    public Stream<BlockPos> getPositions(PlacementContext context, RandomSource random, BlockPos pos) {
        double factor = pos.getY() < 0 ? GearConfig.oresInDeepslate() : GearConfig.oresInStone();
        int whole = (int) factor;
        int count = whole + (random.nextDouble() < factor - whole ? 1 : 0);
        if (count == 0) return Stream.empty();
        if (count == 1) return Stream.of(pos);
        Stream.Builder<BlockPos> out = Stream.builder();
        out.add(pos);
        int chunkX = pos.getX() & ~15;
        int chunkZ = pos.getZ() & ~15;
        for (int i = 1; i < count; i++) {
            out.add(new BlockPos(chunkX + random.nextInt(16), pos.getY(), chunkZ + random.nextInt(16)));
        }
        return out.build();
    }

    @Override
    public PlacementModifierType<?> type() {
        return TYPE;
    }
}
