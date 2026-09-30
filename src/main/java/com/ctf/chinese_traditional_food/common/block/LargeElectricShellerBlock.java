package com.ctf.chinese_traditional_food.common.block;

import com.ctf.chinese_traditional_food.common.block.entity.LargeElectricShellerBlockEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.shapes.VoxelShape;
import org.jetbrains.annotations.Nullable;

/**
 * 大型电动脱壳机：和大型磨粉机同一套放大档，只是查脱壳表。
 *
 * @see LargeElectricMillBlock
 */
public class LargeElectricShellerBlock extends AbstractElectricMachineBlock {

    public LargeElectricShellerBlock(Properties properties) {
        super(properties);
    }

    @Override
    protected String containerKey() {
        return "container.chinese_traditional_food.large_electric_sheller";
    }

    @Override
    protected VoxelShape machineShape() {
        return LARGE_MACHINE_SHAPE;
    }

    @Nullable
    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new LargeElectricShellerBlockEntity(pos, state);
    }
}
