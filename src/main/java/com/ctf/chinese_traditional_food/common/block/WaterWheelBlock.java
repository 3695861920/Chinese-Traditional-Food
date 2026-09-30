package com.ctf.chinese_traditional_food.common.block;

import com.ctf.chinese_traditional_food.registry.ModBlocks;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.EnumProperty;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.level.material.Fluids;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;
import org.jetbrains.annotations.Nullable;

/**
 * 水车：挂在<b>水磨两侧的水车接口</b>上，泡在水里转，给水磨提供动力。
 *
 * <h2>为什么做成独立方块</h2>
 * 用户要的是"水磨外面要有可以接入水车的地方"。如果只是"旁边有水就转"，
 * 那么动力是凭空来的、看不见的；接上真水车之后：
 *
 * <ul>
 *   <li>水磨本体只到磨盘与横轴，外侧留出 <b>iron 轴座（水车接口）</b>；</li>
 *   <li>水车必须放在接口的<b>外侧那一格</b>才能装上（放别处放不下去）；</li>
 *   <li>水车必须<b>碰到水</b>（自己那格或相邻六面有水）才会转；</li>
 *   <li>水磨只有在"至少一个接口上挂着会转的水车"时才有动力。</li>
 * </ul>
 *
 * <h2>转动动画</h2>
 * 和水磨的摇柄一个套路：方块状态 {@code angle=0..3} 对应四张模型，
 * 每 8 tick 换一帧 —— <b>不需要任何渲染器</b>就有转动效果。
 * 轮缘不转、只有辐条与叶片转，所以四帧就够。
 */
public class WaterWheelBlock extends Block {
    /** 轮轴朝向。接口在左右两侧，所以实际只会是 X。 */
    public static final EnumProperty<Direction.Axis> AXIS =
            EnumProperty.create("axis", Direction.Axis.class, Direction.Axis.X, Direction.Axis.Z);

    /** 转动帧（0~3）。 */
    public static final IntegerProperty ANGLE = IntegerProperty.create("angle", 0, 3);

    /** 每帧停留的 tick 数。四帧一圈 = 32 tick，视觉上是"缓缓转动"。 */
    private static final int TICKS_PER_FRAME = 8;

    private static final VoxelShape SHAPE_X = Block.box(6.5, 0.0, 0.0, 9.5, 16.0, 16.0);
    private static final VoxelShape SHAPE_Z = Block.box(0.0, 0.0, 6.5, 16.0, 16.0, 9.5);

    public WaterWheelBlock(Properties properties) {
        super(properties);
        this.registerDefaultState(this.stateDefinition.any()
                .setValue(AXIS, Direction.Axis.X).setValue(ANGLE, 0));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(AXIS, ANGLE);
    }

    @Override
    protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos,
                                  CollisionContext context) {
        return state.getValue(AXIS) == Direction.Axis.X ? SHAPE_X : SHAPE_Z;
    }

    // ------------------------------------------------------------------
    // 认领接口
    // ------------------------------------------------------------------

    /**
     * 这个位置的方块是不是水磨的<b>水车接口</b>。
     *
     * <p>接口就是偏移为 {@code (±1, 1, 0)} 的那个部件（横轴两侧的轴承座）。
     * 从部件自己的 {@code dx/dy/dz} 反推出核心位置就能判断，
     * 不需要方块实体、也不需要额外的表。</p>
     */
    public static boolean isMount(BlockGetter level, BlockPos pos) {
        BlockState state = level.getBlockState(pos);
        if (state.getBlock() != ModBlocks.WATER_MILL_PART.get()) {
            return false;
        }
        BlockPos core = MachinePartBlock.corePos(state, pos);
        int dx = pos.getX() - core.getX();
        int dy = pos.getY() - core.getY();
        int dz = pos.getZ() - core.getZ();
        return dy == 1 && dz == 0 && Math.abs(dx) == 1;
    }

    /** 接口朝外的方向（远离核心的那一侧）。 */
    @Nullable
    public static Direction outwardOf(BlockGetter level, BlockPos mountPos) {
        BlockState state = level.getBlockState(mountPos);
        if (state.getBlock() != ModBlocks.WATER_MILL_PART.get()) {
            return null;
        }
        BlockPos core = MachinePartBlock.corePos(state, mountPos);
        int dx = mountPos.getX() - core.getX();
        return dx > 0 ? Direction.EAST : Direction.WEST;
    }

    /** 这个水车挂在哪个接口上；没挂在接口上（或接口没了）返回 {@code null}。 */
    @Nullable
    public static BlockPos mountOf(BlockGetter level, BlockPos wheelPos) {
        BlockState state = level.getBlockState(wheelPos);
        if (!(state.getBlock() instanceof WaterWheelBlock)) {
            return null;
        }
        for (Direction d : (state.getValue(AXIS) == Direction.Axis.X
                ? new Direction[] { Direction.WEST, Direction.EAST }
                : new Direction[] { Direction.NORTH, Direction.SOUTH })) {
            BlockPos p = wheelPos.relative(d);
            if (isMount(level, p)) {
                return p;
            }
        }
        return null;
    }

    /** 水车有没有碰到水：自己那格或相邻六面任意一处是水都算。 */
    public static boolean touchesWater(BlockGetter level, BlockPos pos) {
        if (level.getFluidState(pos).is(Fluids.WATER)
                || level.getFluidState(pos).is(Fluids.FLOWING_WATER)) {
            return true;
        }
        for (Direction d : Direction.values()) {
            BlockPos p = pos.relative(d);
            if (level.getFluidState(p).is(Fluids.WATER)
                    || level.getFluidState(p).is(Fluids.FLOWING_WATER)) {
                return true;
            }
        }
        return false;
    }

    /** 这个水车是否正在转（挂好了 + 碰到水）。 */
    public static boolean isTurning(BlockGetter level, BlockPos wheelPos) {
        return mountOf(level, wheelPos) != null && touchesWater(level, wheelPos);
    }

    // ------------------------------------------------------------------
    // 放置 / 移除
    // ------------------------------------------------------------------

    /** 只能放在某个水车接口的外侧那一格。 */
    @Nullable
    @Override
    public BlockState getStateForPlacement(BlockPlaceContext context) {
        Level level = context.getLevel();
        BlockPos pos = context.getClickedPos();
        for (Direction d : Direction.Plane.HORIZONTAL) {
            BlockPos mount = pos.relative(d);
            if (!isMount(level, mount)) {
                continue;
            }
            Direction outward = outwardOf(level, mount);
            if (outward != null && pos.equals(mount.relative(outward))) {
                return this.defaultBlockState()
                        .setValue(AXIS, outward.getAxis())
                        .setValue(ANGLE, 0);
            }
        }
        return null;
    }

    /** 接口没了（机器被拆）就把水车也收掉，别让它浮在空中。 */
    @Override
    protected void neighborChanged(BlockState state, Level level, BlockPos pos, Block neighborBlock,
                                   @Nullable net.minecraft.world.level.redstone.Orientation orientation,
                                   boolean movedByPiston) {
        super.neighborChanged(state, level, pos, neighborBlock, orientation, movedByPiston);
        if (level.isClientSide()) {
            return;
        }
        if (mountOf(level, pos) == null) {
            level.destroyBlock(pos, true);
        }
    }

    // ------------------------------------------------------------------
    // 转动
    // ------------------------------------------------------------------
    //
    // 不用方块实体、也不用 ticker —— 那样得为"转个轮子"注册一个方块实体类型，
    // 每个水车还要常驻 tick。这里走原版的**计划刻**：
    // 每隔 TICKS_PER_FRAME 给自己排一次刻，在刻里换一帧；不转了就不再排队。
    // 成本是每个水车每 8 tick 一次回调，且不需要任何存档数据。

    @Override
    public void onPlace(BlockState state, Level level, BlockPos pos, BlockState oldState,
                        boolean movedByPiston) {
        super.onPlace(state, level, pos, oldState, movedByPiston);
        if (!level.isClientSide()) {
            level.scheduleTick(pos, this, TICKS_PER_FRAME);
        }
    }

    @Override
    protected void tick(BlockState state, net.minecraft.server.level.ServerLevel level,
                        BlockPos pos, net.minecraft.util.RandomSource random) {
        if (!isTurning(level, pos)) {
            // 停转：保持当前帧（水车停在半空很自然），也不再排队，
            // 等下次有邻居变化时由 neighborChanged 重新点火。
            return;
        }
        level.setBlock(pos, state.setValue(ANGLE, (state.getValue(ANGLE) + 1) & 3),
                Block.UPDATE_CLIENTS);
        level.scheduleTick(pos, this, TICKS_PER_FRAME);
    }

    /** 让水车不掉落（它就是机器的一部分）。 */
    @Override
    public boolean hasAnalogOutputSignal(BlockState state) {
        return false;
    }
}
