package dev.xardas.nekorogear;

import java.util.function.Supplier;

import net.minecraft.tags.TagKey;
import net.minecraft.world.item.Tier;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.level.block.Block;

/** Tool tier of one item, from items.json. Attack damage is set on the item itself, so the tier adds none. */
public record GearTier(int uses, float speed, TagKey<Block> incorrect, int enchantment, Supplier<Ingredient> repair)
        implements Tier {
    @Override
    public int getUses() {
        return uses;
    }

    @Override
    public float getSpeed() {
        return speed;
    }

    @Override
    public float getAttackDamageBonus() {
        return 0;
    }

    @Override
    public TagKey<Block> getIncorrectBlocksForDrops() {
        return incorrect;
    }

    @Override
    public int getEnchantmentValue() {
        return enchantment;
    }

    @Override
    public Ingredient getRepairIngredient() {
        return repair.get();
    }
}
