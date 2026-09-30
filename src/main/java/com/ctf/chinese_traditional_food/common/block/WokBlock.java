package com.ctf.chinese_traditional_food.common.block;

import com.ctf.chinese_traditional_food.common.block.entity.WokBlockEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.shapes.VoxelShape;
import org.jetbrains.annotations.Nullable;

/**
 * 炒锅：坐在炉灶上快炒（规则表 {@code ModRecipes.COOKING}）。
 *
 * <p>造型是一口敞口的圆锅 + 两侧锅耳 + 一把搭在锅沿上的铲子，
 * 高度约 5.6 像素 —— 碰撞箱跟着模型走，玩家可以直接跨过去。</p>
 */
public class WokBlock extends AbstractHeatApplianceBlock {

    private static final VoxelShape SHAPE =
            net.minecraft.world.level.block.Block.box(0.2, 0.0, 0.2, 15.8, 5.6, 15.8);

    public WokBlock(Properties properties) {
        super(properties);
    }

    @Override
    protected String containerKey() {
        return "container.chinese_traditional_food.wok";
    }

    @Override
    protected VoxelShape machineShape() {
        return SHAPE;
    }

    @Nullable
    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new WokBlockEntity(pos, state);
    }
}
