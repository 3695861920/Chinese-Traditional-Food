package com.ctf.chinese_traditional_food.common.block;

import com.ctf.chinese_traditional_food.common.block.entity.SoupPotBlockEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.shapes.VoxelShape;
import org.jetbrains.annotations.Nullable;

/**
 * 汤锅：坐在炉灶上吊汤（规则表 {@code ModRecipes.BOILING}）。
 *
 * <p>造型是一口高高的深筒锅，两侧双耳、盖着盖子、盖钮上冒着热气；
 * 高度约 9.6 像素 —— 比炒锅高、比蒸笼矮，三者摆一起高矮分明。</p>
 */
public class SoupPotBlock extends AbstractHeatApplianceBlock {

    private static final VoxelShape SHAPE =
            Block.box(0.4, 0.0, 0.4, 15.6, 9.6, 15.6);

    public SoupPotBlock(Properties properties) {
        super(properties);
    }

    @Override
    protected String containerKey() {
        return "container.chinese_traditional_food.soup_pot";
    }

    @Override
    protected VoxelShape machineShape() {
        return SHAPE;
    }

    @Nullable
    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new SoupPotBlockEntity(pos, state);
    }
}
