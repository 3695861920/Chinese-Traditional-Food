package com.ctf.chinese_traditional_food.common.block;

import com.ctf.chinese_traditional_food.common.block.entity.ElectricMillBlockEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import org.jetbrains.annotations.Nullable;

/**
 * 电动磨粉机：单方块设备，吃电把谷物磨成粉。
 *
 * <p>每批加工 {@code MachineEnergy.BATCH_SIZE} 个、耗时 {@code BATCH_TICKS} tick，
 * 运行期间每 tick 吃 {@code ENERGY_PER_TICK} FE —— 也就是"8 个一次、每次 10 秒"。
 * 具体数值集中在 {@code MachineEnergy}。</p>
 *
 * <p>必须接上电才会转：把「熔炉发电机」贴着放，或者用管道接过来。</p>
 */
public class ElectricMillBlock extends AbstractElectricMachineBlock {

    public ElectricMillBlock(Properties properties) {
        super(properties);
    }

    @Override
    protected String containerKey() {
        return "container.chinese_traditional_food.electric_mill";
    }

    @Nullable
    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new ElectricMillBlockEntity(pos, state);
    }
}
