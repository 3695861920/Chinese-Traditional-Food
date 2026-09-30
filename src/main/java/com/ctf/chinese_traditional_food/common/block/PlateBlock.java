package com.ctf.chinese_traditional_food.common.block;

import com.ctf.chinese_traditional_food.common.block.entity.PlateBlockEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import org.jetbrains.annotations.Nullable;

/**
 * 餐盘：单份菜的展示方块。
 *
 * <p>把菜摆上去之后，客户端由
 * {@code com.ctf.chinese_traditional_food.client.render.PlateBlockEntityRenderer}
 * 把菜渲染在盘子上方。</p>
 */
public class PlateBlock extends AbstractDishDisplayBlock {
    public PlateBlock(Properties properties) {
        super(properties);
    }

    @Nullable
    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new PlateBlockEntity(pos, state);
    }
}
