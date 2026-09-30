package com.ctf.chinese_traditional_food.common.block;

import com.ctf.chinese_traditional_food.common.block.entity.AbstractProcessorBlockEntity;
import com.ctf.chinese_traditional_food.common.block.entity.WaterMillBlockEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import org.jetbrains.annotations.Nullable;

/** 水磨：放在水边就能把谷物磨成粉。 */
public class WaterMillBlock extends AbstractProcessorBlock {
    public WaterMillBlock(Properties properties) {
        super(properties);
    }

    @Override
    protected String containerKey() {
        return "container.chinese_traditional_food.water_mill";
    }

    @Override
    protected boolean supportsManualCrank() {
        return true;
    }

    @Nullable
    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new WaterMillBlockEntity(pos, state);
    }

    /** 方便从方块拿到方块实体（NeoForge 的常规写法）。 */
    @Nullable
    public static AbstractProcessorBlockEntity be(net.minecraft.world.level.BlockGetter level, BlockPos pos) {
        return level.getBlockEntity(pos) instanceof AbstractProcessorBlockEntity machine ? machine : null;
    }
}
