package com.ctf.chinese_traditional_food.common.block.entity;

import com.ctf.chinese_traditional_food.common.recipe.ProcessRecipes.Kind;
import com.ctf.chinese_traditional_food.registry.ModBlockEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;

/** 蒸笼：坐在炉灶上蒸。 */
public class SteamerBlockEntity extends AbstractHeatProcessorBlockEntity {

    public SteamerBlockEntity(BlockPos pos, BlockState state) {
        this(ModBlockEntities.STEAMER.get(), pos, state);
    }

    public SteamerBlockEntity(BlockEntityType<?> type, BlockPos pos, BlockState state) {
        super(type, pos, state);
    }

    @Override
    protected Kind kind() {
        return Kind.STEAMING;
    }
}
