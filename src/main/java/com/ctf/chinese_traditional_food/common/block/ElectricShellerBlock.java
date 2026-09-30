package com.ctf.chinese_traditional_food.common.block;

import com.ctf.chinese_traditional_food.common.block.entity.ElectricShellerBlockEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import org.jetbrains.annotations.Nullable;

/**
 * 电动脱壳机：单方块设备，吃电给谷物脱壳。
 *
 * <p>和电动磨粉机是同一套机器框架，只有配方表（{@code Kind.SHELLING}）
 * 与外观不同。</p>
 */
public class ElectricShellerBlock extends AbstractElectricMachineBlock {

    public ElectricShellerBlock(Properties properties) {
        super(properties);
    }

    @Override
    protected String containerKey() {
        return "container.chinese_traditional_food.electric_sheller";
    }

    @Nullable
    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new ElectricShellerBlockEntity(pos, state);
    }
}
