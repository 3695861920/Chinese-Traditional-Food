package com.ctf.chinese_traditional_food.common.block.entity;

import com.ctf.chinese_traditional_food.registry.ModBlockEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;

/**
 * 「摆在地上的菜」的方块实体：只存 1 份菜。
 *
 * <p>复用 {@link AbstractDishDisplayBlockEntity} 的存储与同步，
 * 所以存档、客户端同步、方块被破坏时把菜吐出来这些都是白拿的。
 * 渲染不归它管 —— 三维几何由方块状态（{@code shape} 属性）选的方块模型负责。</p>
 */
public class PlacedDishBlockEntity extends AbstractDishDisplayBlockEntity {
    public static final int CAPACITY = 1;

    public PlacedDishBlockEntity(BlockPos pos, BlockState state) {
        this(ModBlockEntities.PLACED_DISH.get(), pos, state);
    }

    public PlacedDishBlockEntity(BlockEntityType<?> type, BlockPos pos, BlockState state) {
        super(type, pos, state, CAPACITY);
    }

    /** 端起这份菜（清空槽位并同步）。 */
    public ItemStack takeDish() {
        ItemStack stack = this.removeDish(0);
        if (!stack.isEmpty()) {
            this.onDishesChanged();
        }
        return stack;
    }
}
