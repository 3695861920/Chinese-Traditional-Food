package com.ctf.chinese_traditional_food.common.block.entity;

import com.ctf.chinese_traditional_food.common.recipe.ProcessRecipes.Kind;
import com.ctf.chinese_traditional_food.registry.ModBlockEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.material.Fluids;

/**
 * 水磨方块实体。
 *
 * <p>动力来源是<b>水</b>：只要有任意一面紧邻水源（水或含水方块），水轮就一直在转，
 * 不需要红石。这样摆在水边就能看到它自己工作。</p>
 */
public class WaterMillBlockEntity extends AbstractProcessorBlockEntity {

    public WaterMillBlockEntity(BlockPos pos, BlockState state) {
        this(ModBlockEntities.WATER_MILL.get(), pos, state);
    }

    public WaterMillBlockEntity(BlockEntityType<?> type, BlockPos pos, BlockState state) {
        super(type, pos, state);
    }

    @Override
    protected Kind kind() {
        return Kind.MILLING;
    }

    @Override
    protected boolean hasPower(Level level) {
        return hasAdjacentWater(level, this.worldPosition);
    }

    /** 六个面里有没有水（含水方块也算）。 */
    public static boolean hasAdjacentWater(Level level, BlockPos pos) {
        for (Direction direction : Direction.values()) {
            var fluid = level.getFluidState(pos.relative(direction));
            if (fluid.is(Fluids.WATER) || fluid.is(Fluids.FLOWING_WATER)) {
                return true;
            }
        }
        // 水磨自己也可以被水淹没（水logged 情形）
        return level.getFluidState(pos).is(Fluids.WATER);
    }
}
