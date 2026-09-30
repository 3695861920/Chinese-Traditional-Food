package com.ctf.chinese_traditional_food.common.block;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.redstone.Orientation;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;
import org.jetbrains.annotations.Nullable;

/**
 * 脱壳机的料斗（多方块的一部分）。
 *
 * <p>本身不存东西 —— 内容一直在下层主体的方块实体里，
 * 这里只是个"让主体变大容量"的部件。所以没有方块实体，也就没有存档负担。</p>
 *
 * <p>必须放在 {@link GrainShellerBlock} 正上方才有效；否则做不了什么，
 * 但也不会报错（方便玩家先摆料斗再摆机器）。</p>
 */
public class GrainShellerHopperBlock extends Block {
    /** 漏斗外形：上宽下窄，用两个盒子近似。 */
    private static final VoxelShape TOP = Block.box(0.0, 6.0, 0.0, 16.0, 8.0, 16.0);
    private static final VoxelShape BOTTOM = Block.box(4.0, 0.0, 4.0, 12.0, 6.0, 12.0);
    private static final VoxelShape SHAPE = Shapes.or(TOP, BOTTOM);

    public GrainShellerHopperBlock(Properties properties) {
        super(properties);
    }

    @Override
    protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos,
                                  CollisionContext context) {
        return SHAPE;
    }

    /** 下方不是脱壳机主体时不允许放置（避免到处乱放）。 */
    @Nullable
    @Override
    public BlockState getStateForPlacement(BlockPlaceContext context) {
        BlockPos below = context.getClickedPos().below();
        return context.getLevel().getBlockState(below).getBlock() instanceof GrainShellerBlock
                ? this.defaultBlockState()
                : null;
    }

    /**
     * 主体被拆掉后，悬空的料斗自己掉落，别留在天上。
     *
     * <p>注意 26.1 的签名：第 5 个参数从老的 {@code BlockPos neighborPos}
     * 改成了 {@code @Nullable Orientation}（邻居相对本方块的方向）。
     * 这里用不到方向，但必须跟着改，否则会因为"没有覆写任何父类方法"编译失败。</p>
     */
    @Override
    protected void neighborChanged(BlockState state, Level level, BlockPos pos, Block neighborBlock,
                                   @Nullable Orientation orientation, boolean movedByPiston) {
        super.neighborChanged(state, level, pos, neighborBlock, orientation, movedByPiston);
        if (level.isClientSide()) {
            return;
        }
        if (!(level.getBlockState(pos.below()).getBlock() instanceof GrainShellerBlock)) {
            level.destroyBlock(pos, true);
        }
    }

    /** 不影响红石/邻居的常规更新语义。 */
    @Override
    protected boolean useShapeForLightOcclusion(BlockState state) {
        return true;
    }

    /** 只是为了让 Direction 的引用不显得突兀（模型朝向固定为北）。 */
    public static Direction fixedFacing() {
        return Direction.NORTH;
    }
}
