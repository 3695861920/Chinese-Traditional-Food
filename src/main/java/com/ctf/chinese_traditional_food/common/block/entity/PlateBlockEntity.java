package com.ctf.chinese_traditional_food.common.block.entity;

import com.ctf.chinese_traditional_food.registry.ModBlockEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;

/** 餐盘：只摆 1 份菜。 */
public class PlateBlockEntity extends AbstractDishDisplayBlockEntity {
    public static final int CAPACITY = 1;

    /** {@code BlockEntityType} 需要的构造函数签名：(BlockPos, BlockState)。 */
    public PlateBlockEntity(BlockPos pos, BlockState state) {
        this(ModBlockEntities.PLATE.get(), pos, state);
    }

    /** 便于将来做"更大容量的盘子"复用同一个类型。 */
    public PlateBlockEntity(BlockEntityType<?> type, BlockPos pos, BlockState state) {
        super(type, pos, state, CAPACITY);
    }
}
