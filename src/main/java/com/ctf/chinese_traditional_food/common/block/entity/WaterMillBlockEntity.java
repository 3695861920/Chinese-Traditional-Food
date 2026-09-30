package com.ctf.chinese_traditional_food.common.block.entity;

import com.ctf.chinese_traditional_food.common.block.MachineStructure;
import com.ctf.chinese_traditional_food.common.block.WaterWheelBlock;
import com.ctf.chinese_traditional_food.common.recipe.ProcessRecipes.Kind;
import com.ctf.chinese_traditional_food.registry.ModBlockEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;

/**
 * 水磨方块实体。
 *
 * <p>动力来自<b>真正挂在接口上的水车</b>，而不是凭空判定"旁边有水"：
 * 水磨机身两侧各有一个水车接口（iron 轴座），玩家把水车装在外侧那一格，
 * 水车泡在水里才会转，水磨随之开始磨粉。
 * 所以想让它工作，就得真的搭出一套水力传动。</p>
 *
 * @see WaterWheelBlock
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
        return hasTurningWheel(level, this.worldPosition);
    }

    /**
     * 任意一个水车接口上，是不是挂着一个正在转的水车。
     *
     * <p>接口位置直接从生成出来的结构表里筛（偏移 {@code (±1, 1, 0)}），
     * 所以以后改了机器形状，这里会自动跟着变。</p>
     */
    public static boolean hasTurningWheel(Level level, BlockPos core) {
        for (MachineStructure.Part part : MachineStructure.WATER_MILL) {
            if (part.dy() != 1 || part.dz() != 0 || Math.abs(part.dx()) != 1) {
                continue;
            }
            BlockPos mount = core.offset(part.dx(), part.dy(), part.dz());
            Direction outward = part.dx() > 0 ? Direction.EAST : Direction.WEST;
            BlockPos wheel = mount.relative(outward);
            BlockState state = level.getBlockState(wheel);
            if (state.getBlock() instanceof WaterWheelBlock
                    && WaterWheelBlock.isTurning(level, wheel)) {
                return true;
            }
        }
        return false;
    }
}
