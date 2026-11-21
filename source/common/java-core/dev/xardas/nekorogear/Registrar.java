package dev.xardas.nekorogear;

import java.util.function.Supplier;

import net.minecraft.core.Holder;
import net.minecraft.world.item.ArmorMaterial;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;

/** Registers objects the way the current loader wants; the shared code only says what to register. */
public interface Registrar {
    Supplier<Block> block(String name, Supplier<Block> factory);

    Supplier<Item> item(String name, Supplier<Item> factory);

    Holder<ArmorMaterial> armorMaterial(String name, Supplier<ArmorMaterial> factory);
}
