package com.ctf.chinese_traditional_food.common.block.entity;

import com.ctf.chinese_traditional_food.common.recipe.ProcessRecipes.Kind;
import com.ctf.chinese_traditional_food.registry.ModBlockEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;

/**
 * 汤锅：坐在炉灶上吊汤。
 *
 * <p>规则表见 {@code ModRecipes.BOILING}。</p>
 */
public class SoupPotBlockEntity extends AbstractHeatProcessorBlockEntity {

    public SoupPotBlockEntity(BlockPos pos, BlockState state) {
        this(ModBlockEntities.SOUP_POT.get(), pos, state);
    }

    public SoupPotBlockEntity(BlockEntityType<?> type, BlockPos pos, BlockState state) {
        super(type, pos, state);
    }

    @Override
    protected Kind kind() {
        return Kind.BOILING;
    }
}
