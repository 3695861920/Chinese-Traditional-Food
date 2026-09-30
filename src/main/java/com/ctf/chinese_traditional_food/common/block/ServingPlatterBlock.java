package com.ctf.chinese_traditional_food.common.block;

import com.ctf.chinese_traditional_food.common.block.entity.ServingPlatterBlockEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import org.jetbrains.annotations.Nullable;

/**
 * 大拼盘：2×2 摆 4 份菜的展示方块，用来"摆一桌"。
 *
 * <p>配合 {@code ServingPlatterBlockEntityRenderer} 把槽位 0~3 渲染到四个象限。</p>
 */
public class ServingPlatterBlock extends AbstractDishDisplayBlock {
    public ServingPlatterBlock(Properties properties) {
        super(properties);
    }

    @Nullable
    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new ServingPlatterBlockEntity(pos, state);
    }
}
