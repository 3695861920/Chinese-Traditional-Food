package com.ctf.chinese_traditional_food.common.block.entity;

import com.ctf.chinese_traditional_food.registry.ModBlockEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;

/** 大拼盘：2×2 摆 4 份菜，槽位顺序为 左上、右上、左下、右下。 */
public class ServingPlatterBlockEntity extends AbstractDishDisplayBlockEntity {
    public static final int CAPACITY = 4;

    public ServingPlatterBlockEntity(BlockPos pos, BlockState state) {
        this(ModBlockEntities.SERVING_PLATTER.get(), pos, state);
    }

    public ServingPlatterBlockEntity(BlockEntityType<?> type, BlockPos pos, BlockState state) {
        super(type, pos, state, CAPACITY);
    }
}
