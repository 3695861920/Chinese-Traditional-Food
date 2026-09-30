package com.ctf.chinese_traditional_food.common.block;

import com.ctf.chinese_traditional_food.common.block.entity.LargeElectricMillBlockEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.shapes.VoxelShape;
import org.jetbrains.annotations.Nullable;

/**
 * 大型电动磨粉机：小型机的放大版。
 *
 * <p>造型铺满整格、没有腿部留空，所以碰撞箱是完整的一格。
 * 界面沿用小型机的 {@code ProcessorScreen}（布局完全一样，
 * 只是进度条与电量条的填充比例不同 —— 那两样都是按比例算的，不用改）。</p>
 */
public class LargeElectricMillBlock extends AbstractElectricMachineBlock {

    public LargeElectricMillBlock(Properties properties) {
        super(properties);
    }

    @Override
    protected String containerKey() {
        return "container.chinese_traditional_food.large_electric_mill";
    }

    @Override
    protected VoxelShape machineShape() {
        return LARGE_MACHINE_SHAPE;
    }

    @Nullable
    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new LargeElectricMillBlockEntity(pos, state);
    }
}
