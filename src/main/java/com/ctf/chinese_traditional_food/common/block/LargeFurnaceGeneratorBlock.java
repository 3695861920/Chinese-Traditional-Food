package com.ctf.chinese_traditional_food.common.block;

import com.ctf.chinese_traditional_food.common.block.entity.LargeFurnaceGeneratorBlockEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.shapes.VoxelShape;
import org.jetbrains.annotations.Nullable;

/**
 * 大型熔炉发电机：小型机的放大版。
 *
 * <p>占地仍然是一个方块，但造型<b>铺满整格</b>（没有腿部留空），
 * 碰撞箱也因此是完整的一格；输出与缓冲都按 {@code MachineEnergy} 里的
 * 大型档走。交互（塞燃料 / 开界面 / 取回燃料）与小型机完全一致，
 * 全部继承自 {@link FurnaceGeneratorBlock}。</p>
 */
public class LargeFurnaceGeneratorBlock extends FurnaceGeneratorBlock {

    public LargeFurnaceGeneratorBlock(Properties properties) {
        super(properties);
    }

    @Override
    protected VoxelShape machineShape() {
        return LARGE_MACHINE_SHAPE;
    }

    @Nullable
    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new LargeFurnaceGeneratorBlockEntity(pos, state);
    }
}
