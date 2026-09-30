package com.ctf.chinese_traditional_food.common.block;

import com.ctf.chinese_traditional_food.common.block.entity.AbstractProcessorBlockEntity;
import com.ctf.chinese_traditional_food.common.block.entity.WaterMillBlockEntity;
import com.ctf.chinese_traditional_food.registry.ModBlocks;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import org.jetbrains.annotations.Nullable;

/**
 * 水磨核心：放在水边就能把谷物磨成粉。
 *
 * <p>放下一块就会自动展开成一整台 <b>3×3×3</b> 的水磨：
 * 中心是磨盘（核心），底下一层石台，两侧各一个跨两格高的大水轮，
 * 前后是传动箱。缺零件的话机器不转，会提示“结构不完整”。</p>
 */
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

    @Override
    protected List<MachineStructure.Part> structureParts() {
        return MachineStructure.WATER_MILL;
    }

    @Override
    protected Block partBlock() {
        return ModBlocks.WATER_MILL_PART.get();
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
