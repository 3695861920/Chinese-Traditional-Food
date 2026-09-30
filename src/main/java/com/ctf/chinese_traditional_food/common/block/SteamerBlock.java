package com.ctf.chinese_traditional_food.common.block;

import com.ctf.chinese_traditional_food.common.block.entity.SteamerBlockEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.shapes.VoxelShape;
import org.jetbrains.annotations.Nullable;
/**
 * 蒸笼：坐在炉灶上蒸（规则表 {@code ModRecipes.STEAMING}）。
 *
 * <p>造型是三层叠起来的竹蒸笼，顶上盖着盖子、缝隙里冒白汽；
 * 高度约 11.4 像素。三层是"多出来的一层"，一眼就能和单层的锅区分开。</p>
 */
public class SteamerBlock extends AbstractHeatApplianceBlock {

    private static final VoxelShape SHAPE =
            Block.box(0.6, 0.0, 0.6, 15.4, 11.4, 15.4);

    public SteamerBlock(Properties properties) {
        super(properties);
    }

    @Override
    protected String containerKey() {
        return "container.chinese_traditional_food.steamer";
    }

    @Override
    protected VoxelShape machineShape() {
        return SHAPE;
    }

    @Nullable
    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new SteamerBlockEntity(pos, state);
    }
}
